<?php
$file = "../Model/books/".$_FILES['path']['name'];
move_uploaded_file($_FILES['path']['tmp_name'], $file);
echo $_FILES['path']['size'];
$name = $_FILES['path']['name'];
$size = $_FILES['path']['size'];
$query = "INSERT INTO `books`(`name`, `size`) VALUES ('$name','$size')";
$link = mysqli_connect("193.111.0.203:3306", "darklen", "qwerty", "lendro");
mysqli_query($link, $query) or die("error " . mysqli_error($link)); 
?>