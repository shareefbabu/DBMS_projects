<?php
// public/index.php
require_once __DIR__ . '/../config/db_connect.php';

// Fetch recent items for banner (most recent 8)
$banner_sql = "SELECT item_id, item_name, image_path FROM items WHERE status = 'lost' ORDER BY date_lost DESC, created_at DESC LIMIT 10";
$banner_res = $mysqli->query($banner_sql);

// Fetch all open items for grid (lost)
$grid_sql = "SELECT item_id, item_name, description, category, location_lost, date_lost, image_path, status, created_at 
             FROM items 
             WHERE status = 'lost' 
             ORDER BY created_at DESC, item_id DESC";

$grid_res = $mysqli->query($grid_sql);
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Campus Lost &amp; Found — Home</title>
<link rel="stylesheet" href="assets/css/index.css">
<script src="assets/js/script.js" defer></script>
</head>
<body>

<header class="site-header">
  <div class="top-banner">
    <div class="top-inner">
      <!-- left: UPES logo -->
      <div class="logo-wrap">
        <img src="assets/images/upes.png" alt="UPES" class="brand-logo">
      </div>

      <!-- center: heading -->
      <div class="title-wrap" role="heading" aria-level="1">
        <div class="site-sub">Campus</div>
        <div class="site-main">Lost &amp; Found</div>
      </div>

      <!-- right: admin login circle button -->
      <!-- Note: link goes to admin login (path from public/) -->
      <div class="login-wrap">
        <a href="../admin/login.php" class="admin-login" title="Admin login" aria-label="Admin login">
          <!-- inline SVG user icon -->
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 12c2.761 0 5-2.239 5-5s-2.239-5-5-5-5 2.239-5 5 2.239 5 5 5z" fill="currentColor"/>
            <path d="M4 20c0-3.313 4.686-6 8-6s8 2.687 8 6v1H4v-1z" fill="currentColor"/>
          </svg>
        </a>
      </div>
    </div>
  </div>
</header>

<!-- Banner -->
<section class="banner-wrap" aria-label="Recent lost items">
  <div class="banner-track" id="bannerTrack">
    <?php
    // Render banner items (first pass)
    if ($banner_res && $banner_res->num_rows > 0) {
      while ($row = $banner_res->fetch_assoc()) {
        $img = htmlspecialchars($row['image_path'] ?: 'assets/images/placeholder.png', ENT_QUOTES);
        $name = htmlspecialchars($row['item_name'], ENT_QUOTES);
        echo "<div class=\"banner-item\"><img src=\"{$img}\" alt=\"{$name}\"></div>";
      }
      // reset pointer and run same query again to duplicate for seamless scroll
      $banner_res->data_seek(0);
      while ($row = $banner_res->fetch_assoc()) {
        $img = htmlspecialchars($row['image_path'] ?: 'assets/images/placeholder.png', ENT_QUOTES);
        $name = htmlspecialchars($row['item_name'], ENT_QUOTES);
        echo "<div class=\"banner-item duplicate\"><img src=\"{$img}\" alt=\"{$name}\"></div>";
      }
    } else {
      // fallback single placeholder
      echo '<div class="banner-item"><img src="assets/images/placeholder.png" alt="No items"></div>';
      echo '<div class="banner-item duplicate"><img src="assets/images/placeholder.png" alt="No items"></div>';
    }
    ?>
  </div>
</section>

<!-- Grid of items -->
<main>
  <h2 style="margin-bottom:12px;">Lost items</h2>
  <div class="grid">
    <?php
    if ($grid_res && $grid_res->num_rows > 0) {
      while ($r = $grid_res->fetch_assoc()) {
        $id = (int)$r['item_id'];
        $img = htmlspecialchars($r['image_path'] ?: 'assets/images/placeholder.png', ENT_QUOTES);
        $title = htmlspecialchars($r['item_name'], ENT_QUOTES);
        $cat = htmlspecialchars($r['category'] ?: 'Uncategorized', ENT_QUOTES);
        $loc = htmlspecialchars($r['location_lost'] ?: '-', ENT_QUOTES);
        $date = htmlspecialchars($r['date_lost'] ?: date('Y-m-d'), ENT_QUOTES);
        $rawDesc = trim($r['description'] ?? '');
if ($rawDesc === '') {
  $desc = 'No description provided.';
} else {
  $desc = htmlspecialchars($rawDesc, ENT_QUOTES);
}

echo <<<HTML
        <article class="card">
          <div class="card-thumb"><img src="{$img}" alt="{$title}"></div>
          <div class="card-body">
            <div class="meta">{$cat} • Lost at {$loc}</div>
            <div class="title">{$title}</div>
            <div class="desc">{$desc}</div>
            <div class="cta">
              <a class="btn" href="item_details.php?id={$id}">View Details</a>
              <a class="btn secondary" href="claim_form.php?item_id={$id}">Claim this item</a>
            </div>
          </div>
        </article>
HTML;

      }
    } else {
      echo '<div class="muted">No lost items have been reported yet.</div>';
    }
    ?>
  </div>
</main>

<footer class="credit">Made by Shekhar &amp; Krishna</footer>

</body>
</html>