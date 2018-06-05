'use strict';
var appControllers = angular.module('app.aiarticlectrl', ['ngSanitize']);
 
appControllers.controller('AiArticleCtrl',['$scope', '$state', 'MercueRequests','$sce'
    ,function ($scope,$state,MercueRequests,$sce){
   
   console.log("ai AiArticleCtrl list ctrl...");
    $('#color_pick').minicolors();
    //選取玩圖片事件
    $scope.tagList = [];
	$scope.tag = "";
	var entityList = [];
   init();
   
   function init()
   {
       setTimeout(function(){
            url = url.split("?");
            console.log(url[1]);
            if(url[1] != null){
                console.log("edit mode");		 
                $scope.edit_id = url[1];
                $scope.submitText = "更新"
                $scope.editMode = true;
                loadData();
            }
   
       },300);
   }
   
   $scope.submitText = function(){
       console.log("click");
       console.log($scope.userInput)
       var sendData = {};
       sendData.message = $scope.userInput;
       sendData.model_dir = "/opt/nfs/nlu_system_data/models/system/system_model"

       MercueRequests.cueRequest(function(data, status, headers, config){
		   console.log(data);
           if (data.code == 1) {
				entityList = data.entities;
				console.log(entityList);
				console.log(entityList.length);
				$scope.tagList = entityList;
				console.log("get_entities:"+$scope.tagList.toString());
				$scope.serverText = $scope.userInput;
				reSetTag();
           }else{alert(data.message);}
       },function(data, status, headers, config){
           console.log(data);        
       }, "./ai_entity/entity_get", sendData);    

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
       tagData.tag = $scope.tag;
       tagData.string = selectString;
	   tagData.color = color;
	   tagData.extractor = "ner_mitie";
 
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
    	sendData.message = $scope.userInput;
		sendData.entities = $scope.tagList;
		MercueRequests.cueRequest(function(data, status, headers, config){
		   console.log(data);
           if (data.code == 1) {
				var sendData1 = {};
				sendData1.model_dir = "/opt/nfs/nlu_system_data/models/system/system_model"
	 
				MercueRequests.cueRequest(function(data, status, headers, config){
					console.log(data);
					if (data.code == 1) {
						alert("訓練完成");
					}
				},function(data, status, headers, config){
					console.log(data);        
				}, "./ai_entity/entity_mitie_train", sendData1);	
		   }
		},function(data, status, headers, config){
			console.log(data);        
		}, "./ai_entity/entity_save", sendData); 
   }
   
   function replaceRange(s, start, end, substitute) {
       return s.substring(0, start) + substitute + s.substring(end);
   }
   function reSetTag(){
       angular.forEach($scope.tagList, function(value, key) {
           console.log(value);
           var HtmlTag = "<mark" + " style='background:"+value.color+";margin-bottom:2px ;border-radius: 25px; font-size:9px ; padding: 3px;  border:1px solid #238bd6;'>"+value.tag+"</mark>"
           var myRegExp = new RegExp(value.string, 'g');
           $scope.serverText = $scope.serverText.replace(myRegExp,"<mark class=tag-"+value.tag+" style='margin :1px ;border-radius: 25px;  padding: 3px;  border:1px solid #238bd6;'>"+value.string+HtmlTag+"</mark>" );
           console.log("reSet");
         } );
   }

   function loadData(){
    $http({
        method: 'POST',
        url: './ai_intent/intent_get',
        data: {intent_id:$scope.edit_id}
    }).then(function successCallback(response) {
        console.log(response);
        
        var editData = response.data;
        if(editData.cancel_prompt =! null){
            $scope.cancelText = editData.cancel_prompt.prompt_text;
        }
        if(editData.confirmText =! null){
            $scope.confirmText = editData.confirm_prompt.prompt_text;
        }
        $scope.confirmText = editData.confirm_prompt.prompt_text;
        $scope.responseList = editData.response_prompt;
        $scope.name = editData.intent;
        $scope.utterancesList = editData.sentence;
        $scope.slotsList = 	 editData.slots;
        $scope.create_date = editData.create_date
     
    }, function errorCallback(response) {
        console.log(response);
    });

}
   
}]);
