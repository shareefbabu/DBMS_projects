<?php
// admin/audit_logs.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

if (empty($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

// Simple filtering by action_type (optional)
$filter = trim($_GET['type'] ?? '');

// Base query
if ($filter !== '') {
    $stmt = $mysqli->prepare("
        SELECT l.log_id,
               l.action_type,
               l.action_description,
               l.admin_id,
               l.created_at,
               a.admin_name
        FROM audit_log l
        LEFT JOIN admin a ON l.admin_id = a.admin_id
        WHERE l.action_type = ?
        ORDER BY l.created_at DESC
        LIMIT 500
    ");
    $stmt->bind_param('s', $filter);
} else {
    $stmt = $mysqli->prepare("
        SELECT l.log_id,
               l.action_type,
               l.action_description,
               l.admin_id,
               l.created_at,
               a.admin_name
        FROM audit_log l
        LEFT JOIN admin a ON l.admin_id = a.admin_id
        ORDER BY l.created_at DESC
        LIMIT 500
    ");
}
$stmt->execute();
$res = $stmt->get_result();

// Get distinct action types for filter dropdown
$types_res = $mysqli->query("SELECT DISTINCT action_type FROM audit_log ORDER BY action_type ASC");
$types = $types_res ? $types_res->fetch_all(MYSQLI_ASSOC) : [];
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Audit Logs — Admin</title>
<link rel="stylesheet" href="../public/assets/css/audit_logs.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>

<a class="back" href="dashboard.php">&larr; Back to dashboard</a>

<header>
  <div>
    <h1>Audit Logs</h1>
    <div class="small">Showing latest 500 audit entries</div>
  </div>
</header>

<section class="filter-box">
  <form method="get" class="filter-form">
    <label class="small" for="type">Filter by action:</label>
    <select id="type" name="type">
      <option value="">— All types —</option>
      <?php foreach ($types as $t):
        $rawType = $t['action_type'];
        $at = htmlspecialchars($rawType, ENT_QUOTES);
        $sel = ($filter === $rawType) ? 'selected' : '';
      ?>
        <option value="<?php echo $at; ?>" <?php echo $sel; ?>><?php echo $at; ?></option>
      <?php endforeach; ?>
    </select>
    <button class="btn" type="submit">Filter</button>
    <?php if ($filter !== ''): ?>
      <a class="btn btn-secondary" href="audit_logs.php">Clear</a>
    <?php endif; ?>
  </form>
</section>

<section class="table-wrap">
  <table>
    <thead>
      <tr>
        <th style="width:180px;">Time</th>
        <th style="width:140px;">Action</th>
        <th>Description</th>
        <th style="width:160px;">Admin</th>
        <th style="width:80px;">ID</th>
      </tr>
    </thead>
    <tbody>
      <?php
      if ($res && $res->num_rows) {
          while ($r = $res->fetch_assoc()) {

              $time = htmlspecialchars($r['created_at'], ENT_QUOTES);
              $typeRaw = $r['action_type'] ?? '';
              $typeSafe = htmlspecialchars($typeRaw, ENT_QUOTES);
              $desc = nl2br(htmlspecialchars($r['action_description'], ENT_QUOTES));
              $adminName = htmlspecialchars($r['admin_name'] ?? '-', ENT_QUOTES);
              $logId = (int)$r['log_id'];

              // Map action_type to color class
              $actionClass = '';
              if (stripos($typeRaw, 'add') !== false) {
                  $actionClass = 'action-added';
              } elseif (stripos($typeRaw, 'update') !== false || stripos($typeRaw, 'edit') !== false) {
                  $actionClass = 'action-updated';
              } elseif (stripos($typeRaw, 'claim') !== false || stripos($typeRaw, 'approve') !== false) {
                  $actionClass = 'action-claim';
              } elseif (stripos($typeRaw, 'reject') !== false || stripos($typeRaw, 'delete') !== false) {
                  $actionClass = 'action-reject';
              }

              echo '<tr>';
              echo '<td class="time-cell">' . $time . '</td>';
              echo '<td class="action-cell ' . $actionClass . '">' . $typeSafe . '</td>';
              echo '<td>' . $desc . '</td>';
              echo '<td class="muted">' . $adminName . '</td>';
              echo '<td>' . $logId . '</td>';
              echo '</tr>';
          }
      } else {
          echo '<tr><td colspan="5" class="muted empty-row">No audit records found.</td></tr>';
      }
      ?>
    </tbody>
  </table>
</section>

</body>
</html>