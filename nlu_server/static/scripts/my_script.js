// JavaScript Document

$(function(){
	// loader
	$('body').imagesLoaded({
		background:true
	}, function (){
		$('.loader_page').delay(500).fadeOut();
		$('.banner').addClass('active');
	});
	//animation
	new WOW().init();
});