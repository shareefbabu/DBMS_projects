<?php
// public/item_details.php
require_once __DIR__ . '/../config/db_connect.php';

$placeholder = 'assets/images/placeholder.png';

// Validate item id
if (!isset($_GET['id']) || !is_numeric($_GET['id'])) {
    http_response_code(400);
    echo "Invalid item id.";
    exit;
}
$item_id = (int) $_GET['id'];

// Fetch item details safely
$stmt = $mysqli->prepare("SELECT item_id, item_name, description, category, location_lost, date_lost, image_path, status FROM items WHERE item_id = ?");
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

// helper function for image
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
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Item: <?php echo htmlspecialchars($item['item_name']); ?></title>
<link rel="stylesheet" href="assets/css/item_details.css">
</head>

<body>
<div class="container">

    <a class="back" href="index.php">&larr; Home</a>

    <div class="details-card">

        <div class="details-img">
    <img id="itemImage"
         src="<?php echo $image; ?>" 
         alt="<?php echo htmlspecialchars($item['item_name'], ENT_QUOTES); ?>">
</div>

        <div class="details-info">

            <h2><?php echo htmlspecialchars($item['item_name']); ?></h2>

            <div class="meta">
                <?php echo htmlspecialchars($item['category'] ?: 'Uncategorized'); ?>
                • Lost at
                <?php echo htmlspecialchars($item['location_lost'] ?: '-'); ?>
            </div>

            <div class="desc">
                <?php echo nl2br(htmlspecialchars($item['description'] ?: 'No description provided.')); ?>
            </div>

            <div class="meta" style="margin-top:10px;">
                Date lost: <?php echo htmlspecialchars($item['date_lost'] ?: '-'); ?>
                •
                Status: <?php echo htmlspecialchars($item['status']); ?>
            </div>

            <div style="margin-top:18px;">
                <?php if ($item['status'] === 'lost'): ?>
                    <a class="btn" 
                       href="claim_form.php?item_id=<?php echo $item['item_id']; ?>">
                       Claim this item
                    </a>
                <?php else: ?>
                    <span style="padding:10px 12px;border-radius:6px;background:#e2e8f0;color:#1f2937;font-weight:600;">
                        Status: <?php echo htmlspecialchars($item['status']); ?>
                    </span>
                <?php endif; ?>
            </div>

        </div>
    </div>

</div>
<div class="image-modal" id="imageModal" aria-hidden="true">
    <div class="image-modal-backdrop"></div>
    <div class="image-modal-content" role="dialog" aria-modal="true">
        <button class="image-modal-close" type="button" aria-label="Close image">&times;</button>
        <img src="<?php echo $image; ?>" 
             alt="<?php echo htmlspecialchars($item['item_name'], ENT_QUOTES); ?>">
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function () {
  const img = document.getElementById('itemImage');
  const modal = document.getElementById('imageModal');
  const modalImg = modal.querySelector('img');
  const closeBtn = modal.querySelector('.image-modal-close');
  const backdrop = modal.querySelector('.image-modal-backdrop');

  function openModal() {
    modalImg.src = img.src; // ensure same image
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
  }

  if (img) {
    img.addEventListener('click', openModal);
  }

  closeBtn.addEventListener('click', closeModal);
  backdrop.addEventListener('click', closeModal);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeModal();
    }
  });
});
</script>
</body>
</html>