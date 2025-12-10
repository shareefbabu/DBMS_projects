<?php
// config/db_connect.php
// Simple, reusable MySQLi connection. Adjust credentials if needed.

$db_host = 'localhost';
$db_user = 'root';
$db_pass = '';         // <--- put your MySQL root password here if you set one
$db_name = 'campus_lost_found';

$mysqli = new mysqli($db_host, $db_user, $db_pass, $db_name);

if ($mysqli->connect_errno) {
    // In development it's okay to echo the error. Don't do this in production.
    die("Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error);
}

$mysqli->set_charset('utf8mb4');