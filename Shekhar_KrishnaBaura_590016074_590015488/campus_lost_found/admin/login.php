<?php
// admin/login.php
session_start();
require_once __DIR__ . '/../config/db_connect.php';

// If already logged in, redirect to dashboard
if (!empty($_SESSION['admin_id'])) {
    header('Location: dashboard.php');
    exit;
}

$err = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if ($username === '' || $password === '') {
        $err = 'Please enter username and password.';
    } else {
        // fetch admin row
        $stmt = $mysqli->prepare("SELECT admin_id, admin_name, password FROM admin WHERE username = ? LIMIT 1");
        $stmt->bind_param('s', $username);
        $stmt->execute();
        $res = $stmt->get_result();
        $admin = $res->fetch_assoc();
        $stmt->close();

        if (!$admin) {
            $err = 'Invalid credentials.';
        } else {
            $stored = $admin['password'];

            // Support both bcrypt-hashed passwords and plain text (temporary)
            $ok = false;
            if (strpos($stored, '$2y$') === 0 || strpos($stored, '$2a$') === 0) {
                if (password_verify($password, $stored)) $ok = true;
            } else {
                if ($password === $stored) $ok = true;
            }

            if ($ok) {
                $_SESSION['admin_id'] = (int)$admin['admin_id'];
                $_SESSION['admin_name'] = $admin['admin_name'];
                header('Location: dashboard.php');
                exit;
            } else {
                $err = 'Invalid credentials.';
            }
        }
    }
}
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Admin Login — Campus Lost & Found</title>
  <link rel="stylesheet" href="../public/assets/css/login.css">
  <script src="../public/assets/js/script.js" defer></script>
</head>
<body>
  <div class="container">
    <a class="back" href="../public/index.php">&larr; Back to site</a>

    <div class="login-box" role="main">
      <h2>Admin Login</h2>

      <?php if ($err): ?>
        <div class="errors"><?php echo htmlspecialchars($err); ?></div>
      <?php endif; ?>

      <form method="post" novalidate>
        <div class="field">
          <label for="username">Username</label>
          <input id="username" name="username" type="text"
                 value="<?php echo htmlspecialchars($_POST['username'] ?? ''); ?>">
        </div>

        <div class="field">
          <label for="password">Password</label>
          <input id="password" name="password" type="password">
        </div>

        <button class="btn" type="submit">Sign in</button>
      </form>

      
    </div>
  </div>
</body>
</html>
