<?php
// admin/add_item.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

if (empty($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

$errors = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name       = trim($_POST['item_name'] ?? '');
    $desc       = trim($_POST['description'] ?? '');
    $category   = trim($_POST['category'] ?? '');
    $location   = trim($_POST['location_lost'] ?? '');
    $date_lost  = trim($_POST['date_lost'] ?? '');

    if ($name === '') $errors[] = "Item name is required.";

    // handle image upload optional
    $image_path = null;
    if (!empty($_FILES['image']['name'])) {
        $allowed = ['image/jpeg','image/png','image/jpg'];
        $max = 3 * 1024 * 1024; // 3 MB

        if ($_FILES['image']['error'] !== UPLOAD_ERR_OK) {
            $errors[] = "Error uploading image.";
        } else {
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mime  = finfo_file($finfo, $_FILES['image']['tmp_name']);
            finfo_close($finfo);

            if (!in_array($mime, $allowed)) {
                $errors[] = "Only JPG/PNG images allowed.";
            } elseif ($_FILES['image']['size'] > $max) {
                $errors[] = "Image exceeds 3MB.";
            } else {
                $ext      = pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION);
                $filename = 'img_' . time() . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                $destDir  = __DIR__ . '/../public/assets/images/';
                if (!is_dir($destDir)) mkdir($destDir, 0755, true);
                $destPath = $destDir . $filename;

                if (move_uploaded_file($_FILES['image']['tmp_name'], $destPath)) {
                    $image_path = 'assets/images/' . $filename;
                } else {
                    $errors[] = "Failed to move uploaded image.";
                }
            }
        }
    }

    if (empty($errors)) {
        // Tell triggers which admin is doing this action
        $admin_id = (int) $_SESSION['admin_id'];
        $mysqli->query("SET @current_admin_id = " . $admin_id);

        $ins = $mysqli->prepare("
            INSERT INTO items (item_name, description, category, location_lost, date_lost, image_path, added_by_admin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ");
        $ins->bind_param('ssssssi', $name, $desc, $category, $location, $date_lost, $image_path, $admin_id);

        if ($ins->execute()) {
            // write audit log
            $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
            $desc_log = "Added item: {$name} (id={$ins->insert_id})";
            $type = 'item_added';
            $log->bind_param('ssi', $type, $desc_log, $admin_id);
            $log->execute();
            $log->close();

            $ins->close();
            header('Location: manage_items.php');
            exit;
        } else {
            $errors[] = "DB error while inserting item.";
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Add Item — Admin</title>
<link rel="stylesheet" href="../public/assets/css/add_item.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>


<div class="card">
  <h2>Add New Item</h2>
  <p class="small-muted">Fill in the details for the lost item. You can upload a photo if available.</p>

  <?php if (!empty($errors)): ?>
    <div class="errors">
      <?php foreach ($errors as $e): ?>
        <div><?php echo htmlspecialchars($e); ?></div>
      <?php endforeach; ?>
    </div>
  <?php endif; ?>

  <form method="post" enctype="multipart/form-data" novalidate>
        <div class="form-group">
      <label for="item_name">Item name *</label>
      <input
        id="item_name"
        name="item_name"
        type="text"
        value="<?php echo htmlspecialchars($_POST['item_name'] ?? ''); ?>"
      >
      <div class="error-inline" id="item_name_error" aria-live="polite"></div>
    </div>


    <div>
      <label for="description">Description</label>
      <textarea id="description" name="description" rows="4"><?php
        echo htmlspecialchars($_POST['description'] ?? '');
      ?></textarea>
    </div>

    <div>
      <label for="category">Category</label>
      <input id="category" name="category" type="text"
             value="<?php echo htmlspecialchars($_POST['category'] ?? ''); ?>">
    </div>

    <div>
      <label for="location_lost">Location lost</label>
      <input id="location_lost" name="location_lost" type="text"
             value="<?php echo htmlspecialchars($_POST['location_lost'] ?? ''); ?>">
    </div>

    <div>
      <label for="date_lost">Date lost</label>
      <input id="date_lost" name="date_lost" type="date"
             value="<?php echo htmlspecialchars($_POST['date_lost'] ?? ''); ?>">
    </div>

    <div>
      <label for="image">Image (JPG/PNG, max 3MB) (optional)</label>
      <input id="image" name="image" type="file" accept=".jpg,.jpeg,.png">
    </div>

    <div class="row-actions">
  <button class="btn" type="submit">Add item</button>
  <a class="btn-secondary" href="manage_items.php">Cancel</a>
</div>

  </form>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  if (!form) return;

  const fields = [
    {
      input: document.getElementById('item_name'),
      errorEl: document.getElementById('item_name_error'),
      message: 'Please enter an item name.'
    }
  ];

  function clearError(field) {
    if (!field || !field.input) return;
    field.input.classList.remove('field-error');
    if (field.errorEl) field.errorEl.textContent = '';
  }

  // live clear on typing
  fields.forEach(field => {
    if (!field.input) return;
    field.input.addEventListener('input', function () {
      clearError(field);
    });
  });

  form.addEventListener('submit', function (e) {
    let hasError = false;

    fields.forEach(field => {
      if (!field.input) return;
      const value = field.input.value.trim();
      if (value === '') {
        hasError = true;
        field.input.classList.add('field-error');
        if (field.errorEl) {
          field.errorEl.textContent = field.message;
        }
      } else {
        clearError(field);
      }
    });

    if (hasError) {
      e.preventDefault();
      const firstError = fields.find(f => f.input && f.input.classList.contains('field-error'));
      if (firstError && firstError.input) {
        firstError.input.focus();
      }
    }
  });
});
</script>

</body>
</html>