<?php
// admin/view_claim.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';
if (empty($_SESSION['admin_id'])) { header('Location: login.php'); exit; }

if (!isset($_GET['id']) || !is_numeric($_GET['id'])) { echo "Invalid claim id"; exit; }
$id = (int)$_GET['id'];

$stmt = $mysqli->prepare("SELECT c.*, i.item_name, i.image_path, i.status AS item_status FROM claims c JOIN items i ON c.item_id = i.item_id WHERE c.claim_id = ?");
$stmt->bind_param('i', $id);
$stmt->execute();
$claim = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$claim) { echo "Claim not found."; exit; }

$proof = $claim['proof_path'] && file_exists(__DIR__ . '/../public/' . $claim['proof_path']) ? '../public/' . htmlspecialchars($claim['proof_path']) : null;
$image = $claim['image_path'] && file_exists(__DIR__ . '/../public/' . $claim['image_path']) ? '../public/' . htmlspecialchars($claim['image_path']) : '../public/assets/images/placeholder.png';
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Claim #<?php echo (int)$claim['claim_id']; ?> — Admin View</title>
<link rel="stylesheet" href="../public/assets/css/view_claim.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>
<div class="wrap">
  <a class="back" href="manage_claims.php">&larr; Back to claims</a>
  <div class="card">
    <h2>Claim #<?php echo (int)$claim['claim_id']; ?> — <?php echo htmlspecialchars($claim['item_name']); ?></h2>
    <div class="meta">Submitted: <?php echo htmlspecialchars($claim['date_claimed']); ?> • Claim status: <?php echo htmlspecialchars($claim['status']); ?> • Item status: <?php echo htmlspecialchars($claim['item_status']); ?></div>

    <div class="row" style="margin-top:12px;">
      <div class="img"><img src="<?php echo $image; ?>" alt=""></div>
      <div style="flex:1">
        <p><strong>Claimer:</strong> <?php echo htmlspecialchars($claim['claimer_name']); ?></p>
        <p><strong>SAP ID:</strong> <?php echo htmlspecialchars($claim['sap_id']); ?></p>
        <p><strong>Course:</strong> <?php echo htmlspecialchars($claim['course'] ?: '-'); ?></p>
        <p><strong>Message:</strong><br><?php echo nl2br(htmlspecialchars($claim['message'] ?: '-')); ?></p>

        <?php if ($proof): ?>
          <p><strong>Proof file:</strong> <a href="<?php echo $proof; ?>" target="_blank">Open proof</a></p>
        <?php else: ?>
          <p><strong>Proof file:</strong> <span style="color:#6b7280">No proof provided</span></p>
        <?php endif; ?>

        <div style="margin-top:12px;">
          <?php if ($claim['status'] === 'pending'): ?>
            <a class="approve" href="backend/claim_actions.php?action=approve&id=<?php echo (int)$claim['claim_id']; ?>" onclick="return confirm('Approve this claim? This will mark the item as claimed and reject other claims.');">Approve</a>
            <a class="reject" href="backend/claim_actions.php?action=reject&id=<?php echo (int)$claim['claim_id']; ?>" onclick="return confirm('Reject this claim?');" style="margin-left:8px;">Reject</a>
          <?php else: ?>
            <div style="color:#6b7280">This claim has status: <?php echo htmlspecialchars($claim['status']); ?></div>
          <?php endif; ?>
        </div>
      </div>
    </div>
  </div>
</div>
</body>
</html>