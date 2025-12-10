<?php
// public/claim_form.php
require_once __DIR__ . '/../config/db_connect.php';

$placeholder = 'assets/images/placeholder.png';

// Validate item id from GET
if (!isset($_GET['item_id']) || !is_numeric($_GET['item_id'])) {
    http_response_code(400);
    echo "Invalid item id.";
    exit;
}
$item_id = (int) $_GET['item_id'];

// Fetch item to show minimal info
$stmt = $mysqli->prepare("SELECT item_id, item_name, image_path, status FROM items WHERE item_id = ?");
$stmt->bind_param('i', $item_id);
$stmt->execute();
$res = $stmt->get_result();
$item = $res->fetch_assoc();
$stmt->close();

if (!$item) {
    http_response_code(404);
    echo "Item not found.";
    exit;
}
if ($item['status'] !== 'lost') {
    echo "This item is not available for claims (status: " . htmlspecialchars($item['status']) . ").";
    exit;
}

// Handle form POST
$errors = [];
$success = false;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Basic validations
    $claimer_name = trim($_POST['claimer_name'] ?? '');
    $sap_id = trim($_POST['sap_id'] ?? '');
    $course = trim($_POST['course'] ?? '');
    $message = trim($_POST['message'] ?? '');

    if ($claimer_name === '') $errors[] = "Please enter your name.";
    if ($sap_id === '') $errors[] = "Please enter your SAP ID.";
    // course & message optional

    // Handle optional proof upload
    $proof_path = null;
    if (!empty($_FILES['proof']['name'])) {
        $allowed = ['image/jpeg','image/png','application/pdf','image/jpg'];
        $maxBytes = 5 * 1024 * 1024; // 5 MB

        if ($_FILES['proof']['error'] !== UPLOAD_ERR_OK) {
            $errors[] = "Error uploading proof file.";
        } else {
            $finfo = finfo_open(FILEINFO_MIME_TYPE);
            $mime = finfo_file($finfo, $_FILES['proof']['tmp_name']);
            finfo_close($finfo);
            if (!in_array($mime, $allowed)) {
                $errors[] = "Proof must be JPG, PNG or PDF.";
            } elseif ($_FILES['proof']['size'] > $maxBytes) {
                $errors[] = "Proof file exceeds 5 MB limit.";
            } else {
                // generate unique filename and move
                $ext = pathinfo($_FILES['proof']['name'], PATHINFO_EXTENSION);
                $filename = 'proof_' . time() . '_' . bin2hex(random_bytes(6)) . '.' . $ext;
                $destDir = __DIR__ . '/assets/proofs/';
                if (!is_dir($destDir)) mkdir($destDir, 0755, true);
                $destPath = $destDir . $filename;
                if (move_uploaded_file($_FILES['proof']['tmp_name'], $destPath)) {
                    // store relative path for DB (relative to public/)
                    $proof_path = 'assets/proofs/' . $filename;
                } else {
                    $errors[] = "Failed to save proof file.";
                }
            }
        }
    }

    // If no errors, insert claim
    if (empty($errors)) {
        $ins = $mysqli->prepare("INSERT INTO claims (item_id, claimer_name, sap_id, course, message, proof_path) VALUES (?, ?, ?, ?, ?, ?)");
        $ins->bind_param('isssss', $item_id, $claimer_name, $sap_id, $course, $message, $proof_path);
        if ($ins->execute()) {
            // optional: you could insert into audit_log here if triggers aren't set yet.
            $ins->close();
            // redirect to success page
            header("Location: claim_submit_success.php");
            exit;
        } else {
            $errors[] = "Database error while saving claim.";
        }
    }
}

// Helper to show item image path safely
function safe_image($path, $placeholder) {
    if ($path && file_exists(__DIR__ . '/' . $path)) {
        return htmlspecialchars($path, ENT_QUOTES);
    }
    return $placeholder;
}
$image = safe_image($item['image_path'], $placeholder);
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Claim: <?php echo htmlspecialchars($item['item_name']); ?></title>
  <link rel="stylesheet" href="assets/css/claim_form.css">
  <script src="assets/js/script.js" defer></script>
</head>
<body>
<div class="container">
  <a class="back" href="index.php">&larr; Home</a>
  <div class="card">
    <div style="display:flex;align-items:center;gap:12px;">
      <div class="thumb"><img src="<?php echo $image; ?>" alt=""></div>
      <div>
        <div style="font-weight:700;"><?php echo htmlspecialchars($item['item_name']); ?></div>
        <div class="muted">Filing a claim will store your details for in-person verification.</div>
      </div>
    </div>

    <?php if (!empty($errors)): ?>
      <div class="errors">
        <?php foreach ($errors as $e) echo '<div>' . htmlspecialchars($e) . '</div>'; ?>
      </div>
    <?php endif; ?>

    <form method="post" enctype="multipart/form-data" novalidate>
      <input type="hidden" name="item_id" value="<?php echo $item_id; ?>"/>
      <div class="form-field">
  <label for="claimer_name">Your full name *</label>
  <input id="claimer_name" name="claimer_name" type="text" value="<?php echo htmlspecialchars($_POST['claimer_name'] ?? ''); ?>" required>
  <div class="field-error"></div>
</div>

      <div class="form-field">
  <label for="sap_id">SAP ID *</label>
  <input id="sap_id" name="sap_id" type="text" value="<?php echo htmlspecialchars($_POST['sap_id'] ?? ''); ?>" required>
  <div class="field-error"></div>
</div>

      <div>
        <label for="course">Course (optional)</label>
        <input id="course" name="course" type="text" value="<?php echo htmlspecialchars($_POST['course'] ?? ''); ?>">
      </div>

      <div>
        <label for="message">Short message / proof (optional)</label>
        <textarea id="message" name="message" rows="4"><?php echo htmlspecialchars($_POST['message'] ?? ''); ?></textarea>
      </div>

      <div>
        <label for="proof">Upload proof (JPG/PNG/PDF, max 5MB) (optional)</label>
        <input id="proof" name="proof" type="file" accept=".jpg,.jpeg,.png,.pdf">
      </div>

      <div style="margin-top:6px;">
        <button type="submit" class="btn">Submit Claim</button>
      </div>
    </form>
  </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {

  const form = document.querySelector('form');
  const submitBtn = form.querySelector('.btn');

  const nameField = document.getElementById('claimer_name');
  const sapField = document.getElementById('sap_id');

  let attempted = false; // has user tried to submit at least once?

  function clearErrors(){
    [nameField, sapField].forEach(field => {
      field.classList.remove('error');
      const err = field.parentElement.querySelector('.field-error');
      if (err) err.textContent = "";
    });
  }

  // showErrors = true when user actually clicked submit
  function validate(showErrors){
    clearErrors();

    const nameEmpty = nameField.value.trim() === "";
    const sapEmpty  = sapField.value.trim() === "";

    let valid = !nameEmpty && !sapEmpty;

    if (showErrors) {
      if (nameEmpty) {
        nameField.classList.add('error');
        nameField.parentElement.querySelector('.field-error').textContent = "Required";
      }
      if (sapEmpty) {
        sapField.classList.add('error');
        sapField.parentElement.querySelector('.field-error').textContent = "Required";
      }
    }

    // button visual state
    if (valid) {
      submitBtn.classList.add('active');   // remove gray look
    } else {
      submitBtn.classList.remove('active'); // keep gray look
    }

    return valid;
  }

  // When clicking submit
  submitBtn.addEventListener('click', function(e){
    attempted = true;                      // now we are allowed to show errors
    const ok = validate(true);            // validate and show red if needed
    if (!ok) {
      e.preventDefault();                 // block submit if invalid
    }
  });

  // When typing in fields, only update if we've already tried once
  function handleInput(){
    if (attempted) {
      validate(true);   // update errors + button state while fixing
    } else {
      validate(false);  // just update button state, no red yet
    }
  }

  nameField.addEventListener('input', handleInput);
  sapField.addEventListener('input', handleInput);

  // initial state: no errors, gray button
  validate(false);

});
</script>

</body>
</html>