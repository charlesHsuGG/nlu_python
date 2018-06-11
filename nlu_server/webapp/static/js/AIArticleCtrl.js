'use strict';
var appControllers = angular.module('app.aiarticlectrl', ['ngSanitize']);
 
appControllers.controller('AiArticleCtrl',['$http','$scope', '$state', 'MercueRequests','$sce'
    ,function ($http,$scope,$state,MercueRequests,$sce){
   
   console.log("ai AiArticleCtrl list ctrl...");
    $('#color_pick').minicolors();
    //選取玩圖片事件
    $scope.tagList = [];
	$scope.tag = "";
    var entityList = [];
    $scope.admin_id = "40w9dse0277455f634fw40439sd";
    $scope.model_id = "024a140e177851ea83a36ef0ed9b1ddd";
   init();
   
   function init()
   {
            var url = location.href.toString(); 
            console.log(url);
            url = url.split("?");
            console.log(url[1]);
            if(url[1] != null){
                console.log("edit mode");		 
                $scope.edit_id = url[1];
                $scope.editMode = true;
                loadData();
            }
   }
   
   $scope.submitText = function(){
       console.log("click");
       console.log($scope.userInput)
       var sendData = {};
       sendData.message = $scope.userInput;
       sendData.admin_id = $scope.admin_id;
       sendData.model_id = $scope.model_id;

       $http({
            method: 'POST',
            url: "./ai_entity/entity_extractor",
            data: sendData
        }).then(function successCallback(response) {
            console.log(response);
            
            var editData = response.data;
            
            console.log(editData);
            if (editData.code == 1) {
                    entityList = editData.entities;
                    console.log(entityList);
                    console.log(entityList.length);
                    $scope.tagList = entityList;
                    console.log("get_entities:"+$scope.tagList.toString());
                    $scope.serverText = $scope.userInput;
                    reSetTag();
            }else{alert(editData.message);}
            
        }, function errorCallback(response) {
            console.log(response);
        });
   }    
 
   
   $scope.trustAsHtml = function(string) {
       console.log(string);
       return $sce.trustAsHtml(string);
   };
   
   $scope.tagText = function() {
       console.log( $scope.tag);
   if($scope.tag == null || $scope.tag == ""){
       alert("請先填入標籤內容");
       return
   }
   var selectData= getselecttext();
   console.log(selectData);
    var selectRange = selectData.textRange;
    var selectString = selectData.string;
   //取代反白文字
   var color = $("#color_pick").val();
   
   //建立tagList
   var tagData = {};
       tagData.entity = $scope.tag;
       tagData.value = selectString;
	   tagData.color = color;
	   tagData.value_from = "user";
 
       $scope.tagList.push(tagData);
       
       console.log($scope.tagList);
       $scope.serverText = $scope.userInput;
   //覆蓋新的html
   
   reSetTag();
   console.log(selectString);
 
   };
   //取得反白文字
   function getselecttext(){
         var t='';
         if(window.getSelection){t=window.getSelection();}
         else if(document.getSelection){t=document.getSelection();}
         else if(window.document.selection){t=window.document.selection.createRange().text;}
         if(t!='') {
             console.log(t); 
             console.log(t.anchorOffset); 
             console.log(t.focusOffset);
             var selectData = {};
             var textRange = [];
             console.log(t);
             textRange[0] =  t.anchorOffset;
             textRange[1] =  t.focusOffset;
             selectData.textRange =textRange;
             selectData.string = t.toString();
             return selectData;
         }
       
       }
   
   $scope.deleteTag = function(index){
       console.log("delete");
       $scope.serverText = $scope.userInput;
       console.log($scope.tagList[index].tag)
       //$(".tag-"+$scope.tagList[index].tag).replaceWith( $scope.tagList[index].string );
       $scope.tagList.splice(index,1);
       reSetTag();
       console.log($scope.serverText);
       console.log(tag);
   }

   $scope.sendText = function(){
		console.log("send");
        var sendData = {};
        sendData.admin_id = $scope.admin_id;
        sendData.model_id = $scope.model_id;
        sendData.article_title = $scope.textTitle;
    	sendData.article_content = $scope.userInput;
        sendData.entities = $scope.tagList;
        var posturl = "./ai_entity/article_save";
        if($scope.editMode == true){
            posturl = "./ai_entity/article_update";
            sendData.article_id = $scope.edit_id;
			sendData.create_date = $scope.create_date
        }
        console.log(sendData);

        $http({
            method: 'POST',
            url: posturl,
            data: sendData
        }).then(function successCallback(response) {
            console.log(response);
            
            var editData = response.data;
            
            if (editData.code == 1) {
                alert("更新完成");
                $state.go("page",{page:"ai_article_list"});
		   }
         
        }, function errorCallback(response) {
            console.log(response);
        });
   }
   
   function replaceRange(s, start, end, substitute) {
       return s.substring(0, start) + substitute + s.substring(end);
   }
   function reSetTag(){
       angular.forEach($scope.tagList, function(value, key) {
           console.log(value);
           if ('color' in value == false) {
                value.color = "#1E90FF";
           }
           var HtmlTag = "<mark" + " style='background:"+value.color+";margin-bottom:2px ;border-radius: 25px; font-size:9px ; padding: 3px;  border:1px solid #238bd6;'>"+value.entity+"</mark>"
           var myRegExp = new RegExp(value.value, 'g');
           $scope.serverText = $scope.serverText.replace(myRegExp,"<mark class=tag-"+value.entity+" style='margin :1px ;border-radius: 25px;  padding: 3px;  border:1px solid #238bd6;'>"+value.value+HtmlTag+"</mark>" );
           console.log("reSet");
         } );
   }

   function loadData(){
    $http({
        method: 'POST',
        url: './ai_entity/article_get',
        data: {article_id:$scope.edit_id}
    }).then(function successCallback(response) {
        console.log(response);
        
        var editData = response.data;
        
        entityList = editData.entities;
        console.log(entityList);
        console.log(entityList.length);
        $scope.tagList = entityList;
        $scope.create_date = editData.create_date
        console.log("get_entities:"+$scope.tagList.toString());
        $scope.userInput = editData.article_content;
        $scope.serverText = editData.article_content;
        $scope.textTitle = editData.article_title
        $scope.admin_id = editData.admin_id;
        $scope.model_id = editData.model_id;
        reSetTag();
     
    }, function errorCallback(response) {
        console.log(response);
    });

}
   
}]);
