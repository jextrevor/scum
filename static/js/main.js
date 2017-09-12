var socket = io.connect(window.location.protocol+'//'+document.domain+':'+location.port+'/main',{});
players = 0
player = 0
playerpos = []
card = 0
playernames = []
stacks = []
me = 0
playmode = false
function decode(card){
	if(card == 11){
		return "J";
	}
	if(card == 12){
		return "Q";
	}
	if(card == 13){
		return "K";
	}
	if(card == 14){
		return "A";
	}
	return card;
}
function updateplayersrow(){
	document.getElementById("playersrow").innerHTML = "";
	for(var i = 0; i < players; i++){
		document.getElementById("playersrow").innerHTML+="<td class='pla' width='(100/"+players+")%' id='table"+playerpos[i]+"'>"+playernames[playerpos[i]]+"</td>";
	}
	if(players > 0){
	var old = document.getElementById("table"+player).innerHTML;
	document.getElementById("table"+player).innerHTML = "<b>"+old+"</b>";
	old = document.getElementById("table"+me).innerHTML;
	document.getElementById("table"+me).innerHTML = "<i>"+old+"</i>";
	}
}
socket.on("connect", function(){
	var log = document.getElementById("log");
	var newItem = document.createElement("DIV");
	var textnode = document.createTextNode("You have been connected!");
	newItem.appendChild(textnode);
	log.insertBefore(newItem, log.childNodes[0]);
});
socket.on("disconnect", function(){
	var log = document.getElementById("log");
	var newItem = document.createElement("DIV");
	var textnode = document.createTextNode("You have been disconnected!");
	newItem.appendChild(textnode);
	log.insertBefore(newItem, log.childNodes[0]);
});
socket.on("message", function(msg){
	var log = document.getElementById("log");
	var newItem = document.createElement("DIV");
	var textnode = document.createTextNode(msg);
	newItem.appendChild(textnode);
	log.insertBefore(newItem, log.childNodes[0]);
});
socket.on("players",function(json){
	document.getElementById("players").innerHTML=json["players"]
	players = json["players"]
});
socket.on("player",function(json){
	player = json["player"]
	updateplayersrow();
	if(card == 1 && player == me){
		document.getElementById("content").innerHTML = "Choose a card to pass";
	}
	else if(card > 0){
		document.getElementById("content").innerHTML = decode(card);
	}
	else{
		document.getElementById("content").innerHTML = "";
	}
});
socket.on("card",function(json){
	card = json["card"]
	if(card == 1 && player == me){
		document.getElementById("content").innerHTML = "Choose a card to pass";
	}
	else if(card > 0){
		document.getElementById("content").innerHTML = decode(card);
	}
	else{
		document.getElementById("content").innerHTML = "";
	}
});
socket.on("playernames",function(json){
	document.getElementById("playernames").innerHTML = "";
	document.getElementById("join").innerHTML = "";
	playernames = json["playernames"];
	for(var i = 0; i < json["playernames"].length; i++){
		document.getElementById("playernames").innerHTML += "Current name: "+json["playernames"][i]+"<input type='text' id='playername"+i+"' /><button onclick='dochangename("+i+")'>Change Name</button><br />";
		document.getElementById("join").innerHTML += "<button onclick='dojoin("+i+")'>Join as "+(i+1)+"</button><br />";
	}
});
socket.on("playerpos",function(json){
	playerpos = json["playerpos"];
	updateplayersrow();
});
socket.on("hands",function(json){
	
	stacks = json["stacks"]
	document.getElementById("cardsrow").innerHTML = "";
	for(var i = 0; i < stacks[me].length; i++){
		document.getElementById("cardsrow").innerHTML += "<td class='card' width='(100/"+stacks[me].length+")%' >"+decode(stacks[me][i])+"</td>";
	}
});
function doplayers(){
	socket.emit('players',{players:document.getElementById("number").value});
}
function dojoin(number){
	me = number;
	document.getElementById("landing").style.display = "none";
	document.getElementById("play").style.display = "block";
	var log = document.getElementById("log");
	var newItem = document.createElement("DIV");
	var textnode = document.createTextNode("Joining as player "+(number+1)+".");
	newItem.appendChild(textnode);
	log.insertBefore(newItem, log.childNodes[0]);
	if(card == 1 && player == me){
		document.getElementById("content").innerHTML = "Choose a card to pass";
	}
	else if(card > 0){
		document.getElementById("content").innerHTML = decode(card);
	}
	else{
		document.getElementById("content").innerHTML = "";
	}
	document.getElementById("cardsrow").innerHTML = "";
	for(var i = 0; i < stacks[me].length; i++){
		document.getElementById("cardsrow").innerHTML += "<td class='card' onclick='docard("+stacks[me][i]+")' width='(100/"+stacks[me].length+")%' >"+decode(stacks[me][i])+"</td>";
	}
	updateplayersrow();
}
function dochangename(number){
	socket.emit('name',{"number":number,"name":document.getElementById("playername"+number).value});
}
function docard(number){

}
function dopass(){

}
function dodouble(){

}
function dotriple(){

}
function doquad(){
	
}