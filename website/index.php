
<html>
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<script src="https://unpkg.com/sweetalert/dist/sweetalert.min.js"></script>
		<link href="https://fonts.googleapis.com/css?family=Josefin+Sans" rel="stylesheet">
		<link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
		<link href='https://fonts.googleapis.com/css?family=Lato:300,400,700' rel='stylesheet' type='text/css'>
		<link rel="stylesheet" href="style.css" />
		<link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet">
		<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
		<script src="https://unpkg.com/sweetalert/dist/sweetalert.min.js"></script>
		<script defer src="https://use.fontawesome.com/releases/v5.0.12/js/all.js" integrity="sha384-Voup2lBiiyZYkRto2XWqbzxHXwzcm4A5RfdfG6466bu5LqjwwrjXCMBQBLMWh7qR" crossorigin="anonymous"></script>
		<script src='https://www.google.com/recaptcha/api.js'></script>
        <style>

            th, td {
                text-align: center;
                padding: 8px;
            }

        </style>
    </head>
	<header>
		<title>
			Outcast: The Game
		</title>
	</header>
	<body>
		<nav class="navbar navbar-expand-lg navbar-light bg-light menubar" style="z-index: 3;">
		  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
		    <span class="navbar-toggler-icon"></span>
		  </button>
		  <div class="collapse navbar-collapse" id="navbarNav">
		    <ul class="nav navbar-nav">
		      <li class="nav-item"><a class = "nav-link" href="#top">Home</a></li>
  		      <li class="nav-item"><a class = "nav-link" href="https://github.com/davesoftllc/enginez">Download</a></li>
		    </ul>
		  </div>
		</nav>
		<div id="top">
			<div class="vertical-center">
		  		<div class="container" id="hero-text">
		    		<h1 class="display-2">outcast: the game</h1>
		    		<h1 class="display-1">ics3u fse</h1>
		  		</div>
			</div>
		</div>
		<div class="container">
			<div class="row justify-content-md-center">
				<div class="col col-sm-12" id="center-text">
					<h1>Leaderboard</h1>
				</div>
			</div>
			<div class="row justify-content-md-center">
				<div class="col-sm-8">
				<table border = 1 cellpadding = 5 style = "font-family: Calibri; color: #000000;" class="table table-striped table-bordered table-hover">


<?php
/*ACTUAL CODE HERE*/
include_once('config.php');
$conn = new mysqli($dbservername, $dbusername, $dbpassword, "enginez"); /*Connect to database*/
if ($conn->connect_error) {
	print('Error');
	die(); /* End if database failed to connect */
}
$sql = "SELECT username, highscore FROM `users` ORDER BY highscore DESC;"; /*Query to retrieve usernames and highscores*/
$result = $conn->query($sql);
$rows = $result->fetch_all(); /*Retrieve as an array*/
$conn->close();
$counter = 0;
if ($result->num_rows > 0) {
	foreach ($rows as $row){ /*Loop through each row and print out the formatted table*/
		$counter = $counter + 1;
		$r = "<tr><td>%s</td><td>%s</td></tr>";
		$formatted = sprintf($r,$row[0], $row[1]);
		print($formatted);
	}
		

}
/*END ACTUAL USEFUL CODE*/
?>
</table>
</div>
</div>
</div>
<div id="top">
	<div class="parallax">
  		<div class="container" id="hero-text">
  		</div>
	</div>
</div>
<div class="container">
	<div class="row justify-content-sm-center">
		<div class="col-sm-12">
			<a href="https://github.com/davesoftllc/enginez"><h1 id="center-text">Download Today!</h1></a>
		</div>
	</div>
</div>
</body>
</html>


