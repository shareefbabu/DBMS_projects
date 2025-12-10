<?php
// admin/backend/item_actions.php
session_start();
require_once __DIR__ . '/../../config/db_connect.php';
if (empty($_SESSION['admin_id'])) { header('Location: ../login.php'); exit; }

$action = $_GET['action'] ?? '';
$admin_id = (int)$_SESSION['admin_id'];

if ($action === 'delete' && !empty($_GET['id'])) {
    // Set admin ID for triggers
    $admin_id = (int) $_SESSION['admin_id'];
    $mysqli->query("SET @current_admin_id = " . $admin_id);

    $id = (int)$_GET['id'];
    // fetch item to delete file
    $stmt = $mysqli->prepare("SELECT image_path FROM items WHERE item_id = ?");
    $stmt->bind_param('i',$id); $stmt->execute();
    $row = $stmt->get_result()->fetch_assoc(); $stmt->close();

    // delete DB row (claims will cascade)
    $del = $mysqli->prepare("DELETE FROM items WHERE item_id = ?");
    $del->bind_param('i', $id);
    if ($del->execute()) {
        // delete image file if exists
        if (!empty($row['image_path']) && file_exists(__DIR__ . '/../../public/' . $row['image_path'])) {
            @unlink(__DIR__ . '/../../public/' . $row['image_path']);
        }
        // audit log
        $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
        $desc = "Deleted item id={$id}";
        $type = 'item_deleted';
        $log->bind_param('ssi', $type, $desc, $admin_id); $log->execute(); $log->close();
    }
    header('Location: ../manage_items.php');
    exit;
}

if ($action === 'mark_claimed' && !empty($_GET['id'])) {
    // Set admin ID for triggers
    $admin_id = (int) $_SESSION['admin_id'];
    $mysqli->query("SET @current_admin_id = " . $admin_id);
    $id = (int)$_GET['id'];
    $upd = $mysqli->prepare("UPDATE items SET status = 'claimed' WHERE item_id = ?");
    $upd->bind_param('i', $id);
    if ($upd->execute()) {
        // audit log
        $log = $mysqli->prepare("INSERT INTO audit_log (action_type, action_description, admin_id) VALUES (?, ?, ?)");
        $desc = "Marked item id={$id} as claimed";
        $type = 'item_claimed';
        $log->bind_param('ssi', $type, $desc, $admin_id);
        $log->execute(); $log->close();
    }
    header('Location: ../manage_items.php');
    exit;
}

// default: go back
header('Location: ../manage_items.php');
exit;