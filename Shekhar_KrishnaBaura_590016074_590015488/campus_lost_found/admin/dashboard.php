<?php
// admin/dashboard.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

// Protect page: redirect to login if not authenticated
if (empty($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

$admin_id = (int) $_SESSION['admin_id'];

// Basic stats queries
$total_items = $mysqli->query("SELECT COUNT(*) AS c FROM items")->fetch_assoc()['c'] ?? 0;
$pending_claims = $mysqli->query("SELECT COUNT(*) AS c FROM claims WHERE status = 'pending'")->fetch_assoc()['c'] ?? 0;
$recent_items_res = $mysqli->query("SELECT item_id, item_name, created_at FROM items ORDER BY created_at DESC LIMIT 6");
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Admin Dashboard — Campus Lost & Found</title>
  <link rel="stylesheet" href="../public/assets/css/dashboard.css">
  <script src="../public/assets/js/script.js" defer></script>
</head>
<body>
  <a class="back" href="../public/index.php">&larr; Back to portal</a>
  <div class="page-wrap">

    <header>
      <div>
        <h1>Admin Dashboard</h1>
        <div class="welcome-text">Welcome, <?php echo htmlspecialchars($_SESSION['admin_name']); ?></div>
      </div>
      <div class="header-actions">
        <a class="btn-header primary" href="manage_items.php">Manage Items</a>
        <a class="btn-header secondary" href="manage_claims.php">Manage Claims</a>
        <a class="btn-header secondary" href="audit_logs.php">Audit Logs</a>
        <a class="btn-header danger" href="logout.php">Logout</a>
      </div>

    </header>

    <section class="card-row">
      <div class="card-small">
        <div class="card-label">Total items</div>
        <div class="card-value"><?php echo (int)$total_items; ?></div>
      </div>
      <div class="card-small">
        <div class="card-label">Pending claims</div>
        <div class="card-value"><?php echo (int)$pending_claims; ?></div>
      </div>
    </section>

    <section class="table-wrap">
      <h3 class="section-title">Recently added items</h3>
      <table>
        <thead>
          <tr>
            <th style="width:60px;">ID</th>
            <th>Item</th>
            <th style="width:190px;">Added</th>
          </tr>
        </thead>
        <tbody>
          <?php
          if ($recent_items_res && $recent_items_res->num_rows) {
              while ($r = $recent_items_res->fetch_assoc()) {
                  echo '<tr>';
                  echo '<td>' . (int)$r['item_id'] . '</td>';
                  echo '<td>' . htmlspecialchars($r['item_name']) . '</td>';
                  echo '<td>' . htmlspecialchars($r['created_at']) . '</td>';
                  echo '</tr>';
              }
          } else {
              echo '<tr><td colspan="3" class="muted-cell">No items yet</td></tr>';
          }
          ?>
        </tbody>
      </table>
    </section>

  </div>
</body>
</html>