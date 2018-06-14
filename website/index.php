<?php
include_once('config.php');
$conn = new mysqli($dbservername, $dbusername, $dbpassword, "enginez");
if ($conn->connect_error) {
	print('Error');
	die()
}

$sql = "SELECT username, highscore FROM `users`";
$result = $conn->query($sql);
$rows = $result->fetch_array();
$conn->close();
if ($result->num_rows > 0) {
	foreach ($rows as $row)
		print($row['username']);
		print($row['highscore']);
}
?>
<html>
<head>
	<title>High Score</title>
</head>
<body>
<h1>Players</h1>
</body>
</html>