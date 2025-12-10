<?php
// admin/manage_claims.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

if (empty($_SESSION['admin_id'])) {
    header('Location: login.php');
    exit;
}

// Fetch claims (most recent first)
$sql = "
    SELECT
        c.claim_id,
        c.item_id,
        c.claimer_name,
        c.sap_id,
        c.course,
        c.message,
        c.proof_path,
        c.date_claimed,
        c.status,
        i.item_name
    FROM claims c
    JOIN items i ON c.item_id = i.item_id
    ORDER BY c.date_claimed DESC
";
$res = $mysqli->query($sql);
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Manage Claims — Admin</title>
<link rel="stylesheet" href="../public/assets/css/manage_claims.css">
<script src="../public/assets/js/script.js" defer></script>
</head>
<body>

<a class="back" href="dashboard.php">&larr; Back to Dashboard</a>

<header>
  <div>
    <h1>Manage Claims</h1>
    <div class="muted">Admin: <?php echo htmlspecialchars($_SESSION['admin_name']); ?></div>
  </div>
</header>


<section class="table-wrap">
  <table>
    <thead>
      <tr>
        <th style="width:80px;">Claim ID</th>
        <th>Item</th>
        <th>Claimer</th>
        <th>SAP ID</th>
        <th>Course</th>
        <th style="width:160px;">Submitted</th>
        <th style="width:110px;">Status</th>
        <th style="width:220px;">Actions</th>
      </tr>
    </thead>
    <tbody>
<?php
if ($res && $res->num_rows) {
    while ($r = $res->fetch_assoc()) {
        $id      = (int)$r['claim_id'];
        $item    = htmlspecialchars($r['item_name'], ENT_QUOTES);
        $itemId  = (int)$r['item_id'];
        $claimer = htmlspecialchars($r['claimer_name'], ENT_QUOTES);
        $sap     = htmlspecialchars($r['sap_id'], ENT_QUOTES);
        $course  = htmlspecialchars($r['course'] ?: '-', ENT_QUOTES);
        $date    = htmlspecialchars($r['date_claimed'], ENT_QUOTES);

        $status_raw  = $r['status'] ?? '';
        $status_safe = htmlspecialchars($status_raw, ENT_QUOTES);

        // map status -> badge class
        $badgeClass = 'badge';
        if ($status_raw === 'pending') {
            $badgeClass .= ' pending';
        } elseif ($status_raw === 'approved') {
            $badgeClass .= ' approved';
        } elseif ($status_raw === 'rejected') {
            $badgeClass .= ' rejected';
        }

        echo '<tr>';
        echo '<td>' . $id . '</td>';
        echo '<td>' . $item . ' (id: ' . $itemId . ')</td>';
        echo '<td>' . $claimer . '</td>';
        echo '<td>' . $sap . '</td>';
        echo '<td>' . $course . '</td>';
        echo '<td>' . $date . '</td>';
        echo '<td><span class="' . $badgeClass . '">' . $status_safe . '</span></td>';

        echo '<td class="actions">';
        echo '<a class="btn view" href="view_claim.php?id=' . $id . '">View</a>';
        if ($status_raw === 'pending') {
            echo '<a class="btn approve" href="backend/claim_actions.php?action=approve&id=' . $id . '" ';
            echo 'onclick="return confirm(\'Approve this claim? This will mark the item as claimed and reject other claims.\')">Approve</a>';
            echo '<a class="btn reject" href="backend/claim_actions.php?action=reject&id=' . $id . '" ';
            echo 'onclick="return confirm(\'Reject this claim?\')">Reject</a>';
        }
        echo '</td>';

        echo '</tr>';
    }
} else {
    echo '<tr><td colspan="8" class="empty-row">No claims found.</td></tr>';
}
?>
    </tbody>
  </table>
</section>

</body>
</html>