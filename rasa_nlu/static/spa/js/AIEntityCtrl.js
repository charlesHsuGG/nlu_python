'use strict';
var appControllers = angular.module('app.aientityctrl', ['ngSanitize']);

appControllers.controller('AiEntityCtrl', ['$scope', '$state', 'MercueRequests', '$sce'
	, function ($scope, $state, MercueRequests, $sce) {

		console.log("ai AiEntityCtrl list ctrl...");
		$('#color_pick').minicolors();
		//選取玩圖片事件
		$scope.tagList = [];
		$scope.tag = "";
		init();

		function init() {
			setTimeout(function () {


			}, 300);
		}

		$scope.submitText = function () {
			console.log("click");
			console.log($scope.userInput)
			var sendData = {};
			sendData.message = $scope.userInput;
			sendData.model_dir = "/Users/kevin/Desktop/rasa_nlu_chi/models/default/current"
			console.log(sendData);
			//
			MercueRequests.cueRequest(function (data, status, headers, config) {
				console.log(data);
				if (data.code == 1) {

					$scope.serverText = $scope.userInput;
					var entityList = data.entities;
					console.log(entityList);
					console.log(entityList.length);
					$scope.tagList = entityList;
					console.log($scope.tagList);
					reSetTag();
				} else { alert(data.message); }
			}, function (data, status, headers, config) {
				console.log(data);
			}, "../ai/entity_get", sendData);
			//$scope.serverText = $scope.userInput;
		}


		$scope.trustAsHtml = function (string) {
			return $sce.trustAsHtml(string);
		};

		$scope.tagText = function () {
			console.log($scope.tag);
			if ($scope.tag == null || $scope.tag == "") {
				alert("請先填入標籤內容");
				return
			}
			var selectData = getselecttext();
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

			$scope.tagList.push(tagData);

			console.log($scope.tagList);
			$scope.serverText = $scope.userInput;
			//覆蓋新的html

			reSetTag();
			console.log(selectString);

		};
		//取得反白文字
		function getselecttext() {
			var t = '';
			if (window.getSelection) { t = window.getSelection(); }
			else if (document.getSelection) { t = document.getSelection(); }
			else if (window.document.selection) { t = window.document.selection.createRange().text; }
			if (t != '') {
				console.log(t);
				console.log(t.anchorOffset);
				console.log(t.focusOffset);
				var selectData = {};
				var textRange = [];
				console.log(t);
				textRange[0] = t.anchorOffset;
				textRange[1] = t.focusOffset;
				selectData.textRange = textRange;
				selectData.string = t.toString();
				return selectData;
			}

		}

		$scope.deleteTag = function (index) {
			console.log("delete");
			$scope.serverText = $scope.userInput;
			console.log($scope.tagList[index].tag)
			//$(".tag-"+$scope.tagList[index].tag).replaceWith( $scope.tagList[index].string );
			$scope.tagList.splice(index, 1);
			reSetTag();
			console.log($scope.serverText);
			console.log(tag);
		}

		function replaceRange(s, start, end, substitute) {
			return s.substring(0, start) + substitute + s.substring(end);
		}
		function reSetTag() {
			angular.forEach($scope.tagList, function (value, key) {
				console.log(value);
				var HtmlTag = "<mark" + " style='background:" + value.color + ";margin-bottom:2px ;border-radius: 25px; font-size:9px ; padding: 3px;  border:1px solid #238bd6;'>" + value.tag + "</mark>"
				var myRegExp = new RegExp(value.string, 'g');
				$scope.serverText = $scope.serverText.replace(myRegExp, "<mark class=tag-" + value.tag + " style='margin :1px ;border-radius: 25px;  padding: 3px;  border:1px solid #238bd6;'>" + value.string + HtmlTag + "</mark>");
				console.log("reSet");
			});
		}

	}]);

