<?php
// admin/manage_items.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

// protect
if (empty($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

// fetch items + who added them
$items_res = $mysqli->query("
    SELECT i.*, a.admin_name AS added_by
    FROM items i
    LEFT JOIN admin a ON i.added_by_admin = a.admin_id
    ORDER BY i.created_at DESC
");
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Manage Items — Admin</title>
<link rel="stylesheet" href="../public/assets/css/manage_items.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>

<a class="back" href="dashboard.php">&larr; Back to Dashboard</a>

<header>
  <div>
    <h1>Manage Items</h1>
    <div class="small">Admin: <?php echo htmlspecialchars($_SESSION['admin_name']); ?></div>
  </div>
  <div class="header-actions">
    <a class="btn-header primary" href="add_item.php">+ Add Item</a>
  </div>
</header>

<section class="table-wrap">
  <table>
    <thead>
      <tr>
        <th style="width:60px;">ID</th>
        <th style="width:90px;">Image</th>
        <th>Item</th>
        <th>Category</th>
        <th>Location</th>
        <th>Date Lost</th>
        <th>Status</th>
        <th>Added by</th>
        <th style="width:260px;">Actions</th>
      </tr>
    </thead>
    <tbody>
<?php
if ($items_res && $items_res->num_rows) {
    while ($r = $items_res->fetch_assoc()) {
        $id = (int)$r['item_id'];

        // image path (fallback to placeholder)
        $img = '../public/assets/images/placeholder.png';
        if (!empty($r['image_path']) && file_exists(__DIR__ . '/../public/' . $r['image_path'])) {
            $img = '../public/' . htmlspecialchars($r['image_path'], ENT_QUOTES);
        }

        // status badge style
        $status_raw  = $r['status'] ?? '';
        $status_safe = htmlspecialchars($status_raw, ENT_QUOTES);

        $badgeClass = 'badge-default';
        if ($status_raw === 'lost') {
            $badgeClass = 'badge-lost';
        } elseif ($status_raw === 'claimed') {
            $badgeClass = 'badge-claimed';
        }

        echo '<tr>';
        echo '<td>' . $id . '</td>';
        echo '<td><img class="img-thumb" src="' . $img . '" alt=""></td>';
        echo '<td>' . htmlspecialchars($r['item_name']) . '</td>';
        echo '<td>' . htmlspecialchars($r['category'] ?: '-') . '</td>';
        echo '<td>' . htmlspecialchars($r['location_lost'] ?: '-') . '</td>';
        echo '<td>' . htmlspecialchars($r['date_lost'] ?: '-') . '</td>';
        echo '<td><span class="badge ' . $badgeClass . '">' . $status_safe . '</span></td>';
        echo '<td>' . htmlspecialchars($r['added_by'] ?: '-') . '</td>';

        echo '<td class="actions">';
        echo '<a class="btn edit" href="edit_item.php?id=' . $id . '">Edit</a>';
        echo '<a class="btn delete" href="backend/item_actions.php?action=delete&id=' . $id . '" ';
        echo 'onclick="return confirm(\'Delete this item? This will also remove related claims.\')">Delete</a>';
        if ($status_raw !== 'claimed') {
            echo '<a class="btn claims" href="backend/item_actions.php?action=mark_claimed&id=' . $id . '" ';
            echo 'onclick="return confirm(\'Mark this item as claimed?\')">Mark claimed</a>';
        }
        echo '</td>';

        echo '</tr>';
    }
} else {
    echo '<tr><td colspan="9" class="empty-row">No items found.</td></tr>';
}
?>
    </tbody>
  </table>
</section>

</body>
</html>
