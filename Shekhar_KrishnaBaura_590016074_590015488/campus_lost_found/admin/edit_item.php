<?php
// admin/edit_item.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';
if (empty($_SESSION['admin_id'])) { header('Location: login.php'); exit; }

if (!isset($_GET['id']) || !is_numeric($_GET['id'])) {
    echo "Invalid id"; exit;
}
$id = (int)$_GET['id'];

// Fetch item
$stmt = $mysqli->prepare("SELECT * FROM items WHERE item_id = ?");
$stmt->bind_param('i', $id);
$stmt->execute();
$item = $stmt->get_result()->fetch_assoc();
$stmt->close();
if (!$item) { echo "Item not found"; exit; }

$errors = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $name = trim($_POST['item_name'] ?? '');
    $desc = trim($_POST['description'] ?? '');
    $category = trim($_POST['category'] ?? '');
    $location = trim($_POST['location_lost'] ?? '');
    $date_lost = trim($_POST['date_lost'] ?? '');

    if ($name === '') $errors[] = "Item name required.";

    $image_path = $item['image_path']; // keep existing unless replaced
    if (!empty($_FILES['image']['name'])) {
        $allowed = ['image/jpeg','image/png','image/jpg'];
        $max = 3*1024*1024;
        if ($_FILES['image']['error'] !== UPLOAD_ERR_OK) {
            $errors[] = "Error uploading image.";
        } else {
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mime = finfo_file($finfo, $_FILES['image']['tmp_name']);
            finfo_close($finfo);
            if (!in_array($mime, $allowed)) $errors[] = "Only JPG/PNG allowed.";
            elseif ($_FILES['image']['size'] > $max) $errors[] = "Image exceeds 3MB.";
            else {
                $ext = pathinfo($_FILES['image']['name'], PATHINFO_EXTENSION);
                $filename = 'img_' . time() . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                $destDir = __DIR__ . '/../public/assets/images/';
                if (!is_dir($destDir)) mkdir($destDir,0755,true);
                $destPath = $destDir . $filename;
                if (move_uploaded_file($_FILES['image']['tmp_name'], $destPath)) {
                    // delete old file if exists
                    if ($item['image_path'] && file_exists(__DIR__ . '/../public/' . $item['image_path'])) {
                        @unlink(__DIR__ . '/../public/' . $item['image_path']);
                    }
                    $image_path = 'assets/images/' . $filename;
                } else {
                    $errors[] = "Failed to move uploaded image.";
                }
            }
        }
    }

    if (empty($errors)) {
        $admin_id = (int) $_SESSION['admin_id'];
        $mysqli->query("SET @current_admin_id = " . $admin_id);

        $upd = $mysqli->prepare("UPDATE items SET item_name=?, description=?, category=?, location_lost=?, date_lost=?, image_path=? WHERE item_id=?");
        $upd->bind_param('ssssssi', $name, $desc, $category, $location, $date_lost, $image_path, $id);
        if ($upd->execute()) {
            // audit log
            $admin_id = (int)$_SESSION['admin_id'];
            $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
            $desc_log = "Edited item: {$name} (id={$id})";
            $type = 'item_edited';
            $log->bind_param('ssi', $type, $desc_log, $admin_id);
            $log->execute(); $log->close();

            header('Location: manage_items.php'); exit;
        } else {
            $errors[] = "DB error while updating.";
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Edit Item</title>
<link rel="stylesheet" href="../public/assets/css/edit_item.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>
<div class="box">
  <h2>Edit Item (ID: <?php echo (int)$item['item_id']; ?>)</h2>
  <?php if (!empty($errors)): ?><div class="err"><?php foreach ($errors as $e) echo '<div>'.htmlspecialchars($e).'</div>'; ?></div><?php endif; ?>
  <form method="post" enctype="multipart/form-data" novalidate>
    <label>Item name *</label>
    <input name="item_name" type="text" value="<?php echo htmlspecialchars($item['item_name']); ?>">

    <label>Description</label>
    <textarea name="description" rows="4"><?php echo htmlspecialchars($item['description']); ?></textarea>

    <label>Category</label>
    <input name="category" type="text" value="<?php echo htmlspecialchars($item['category']); ?>">

    <label>Location lost</label>
    <input name="location_lost" type="text" value="<?php echo htmlspecialchars($item['location_lost']); ?>">

    <label>Date lost</label>
    <input name="date_lost" type="date" value="<?php echo htmlspecialchars($item['date_lost']); ?>">

    <div style="margin-top:8px;">
      <label>Current image</label>
      <div class="thumb"><img src="<?php echo ($item['image_path'] && file_exists(__DIR__ . '/../public/' . $item['image_path'])) ? '../public/' . htmlspecialchars($item['image_path']) : '../public/assets/images/placeholder.png'; ?>" alt=""></div>
    </div>

    <label>Replace image (optional)</label>
    <input name="image" type="file" accept=".jpg,.jpeg,.png">

    <div style="margin-top:12px;">
      <button class="btn" type="submit">Save changes</button>
      <a class="back" href="manage_items.php">&larr; Back</a>
    </div>
  </form>
</div>
</body>
</html>