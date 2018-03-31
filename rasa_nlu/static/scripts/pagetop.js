$(function(){
		   
	var pagetop_a = '<a href="#" class="pagetop tribes_link"></a>';
	$('body').append( pagetop_a );
	
	var a_pagetop =   $('a.pagetop');

	a_pagetop.on('click', function () {
			$('body, html').stop().animate({
				scrollTop: 0
			}, 400);
			return false;
	});

	$(window).on('load scroll resize', function(){
												 
			  var win_scrollTop = $(window).scrollTop(),//win的scrollTop
			      document_h = $(document).height(),//頁面的總高度
				  win_h = $(window).outerHeight(true),//win的總高度
				  footer_h = $('footer').innerHeight(),//頁尾的總高度
				  tatol_scrollTop = ( document_h - win_h ),//求最大scrollTop表示頁面到頁尾了
				  header_hhh = 82;
				  			

			  var new_win = $(window),
			  	  new_win_w = new_win.innerWidth(),
				  vvv_w = 1023; 
			  
			  //if( new_win_w > vvv_w ){
				  
						  if( win_scrollTop > header_hhh ){
							
							a_pagetop.show().css({
									top: win_h - 40,
									right: 10
							});
									
							if( win_scrollTop > (tatol_scrollTop - footer_h) ){
							
										a_pagetop.css({position: 'absolute'}).stop()
										.animate({
											top: $('footer').offset().top - 70 ,
											right:10
										},0);
							
							}else{
								a_pagetop.css({position: 'fixed'}).stop()
								.animate({
									top: win_h - 70,
									right:10
								},0);
							}
		
								
						}else{
							a_pagetop.stop().fadeOut(1);
						}
				  
			 // }else{
			     // a_pagetop.hide(); //小螢幕就隱藏PC版置頂btn
				 // return false();
			  //}
		  });
});