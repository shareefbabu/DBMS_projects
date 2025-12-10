<?php
// admin/backend/claim_actions.php
session_start();
require_once __DIR__ . '/../../config/db_connect.php';
if (empty($_SESSION['admin_id'])) { header('Location: ../login.php'); exit; }

$action = $_GET['action'] ?? '';
$admin_id = (int)$_SESSION['admin_id'];

if (!in_array($action, ['approve','reject']) || empty($_GET['id']) || !is_numeric($_GET['id'])) {
    header('Location: ../manage_claims.php'); exit;
}
$claim_id = (int)$_GET['id'];

// fetch claim and item
$stmt = $mysqli->prepare("SELECT claim_id, item_id, claimer_name, status FROM claims WHERE claim_id = ?");
$stmt->bind_param('i', $claim_id);
$stmt->execute();
$claim = $stmt->get_result()->fetch_assoc();
$stmt->close();

if (!$claim) {
    header('Location: ../manage_claims.php'); exit;
}

$item_id = (int)$claim['item_id'];

if ($action === 'approve') {
    // Set admin ID for triggers
    $admin_id = (int) $_SESSION['admin_id'];
    $mysqli->query("SET @current_admin_id = " . $admin_id);
    // Start transaction
    $mysqli->begin_transaction();
    try {
        // 1) mark this claim approved
        $upd = $mysqli->prepare("UPDATE claims SET status = 'approved' WHERE claim_id = ?");
        $upd->bind_param('i', $claim_id); $upd->execute(); $upd->close();

        // 2) mark the item as claimed
        $u2 = $mysqli->prepare("UPDATE items SET status = 'claimed' WHERE item_id = ?");
        $u2->bind_param('i', $item_id); $u2->execute(); $u2->close();

        // 3) reject all other claims for this item
        $u3 = $mysqli->prepare("UPDATE claims SET status = 'rejected' WHERE item_id = ? AND claim_id <> ?");
        $u3->bind_param('ii', $item_id, $claim_id); $u3->execute(); $u3->close();

        // 4) audit logs
        $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
        $desc1 = "Approved claim id={$claim_id} for item_id={$item_id}";
        $desc2 = "Marked item id={$item_id} as claimed (via claim {$claim_id})";

        $type = 'claim_approved';
        $log->bind_param('ssi', $type, $desc1, $admin_id);
        $log->execute();

        $type = 'item_claimed';
        $log->bind_param('ssi', $type, $desc2, $admin_id);
        $log->execute();

        $log->close();


        $mysqli->commit();
    } catch (Exception $e) {
        $mysqli->rollback();
        // Optionally write an error log
    }

    header('Location: ../manage_claims.php');
    exit;
}

if ($action === 'reject') {
    // Set admin ID for triggers
    $admin_id = (int) $_SESSION['admin_id'];
    $mysqli->query("SET @current_admin_id = " . $admin_id);
    $upd = $mysqli->prepare("UPDATE claims SET status = 'rejected' WHERE claim_id = ?");
    $upd->bind_param('i', $claim_id); $upd->execute(); $upd->close();

    $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
    $desc = "Rejected claim id={$claim_id}";
    $type = 'claim_rejected';
    $log->bind_param('ssi', $type, $desc, $admin_id);
    $log->execute(); $log->close();

    header('Location: ../manage_claims.php');
    exit;
}

// fallback
header('Location: ../manage_claims.php');
exit;