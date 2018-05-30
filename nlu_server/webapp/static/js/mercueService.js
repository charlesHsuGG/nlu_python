/**
 * 
 */
'use strict';

// Define your services here if necessary
var mercueServices = angular.module('mercue.services', []);

mercueServices.factory('MercueRequests',['$http', '$rootScope' , function($http, $rootScope){
	
	var editAccountBean = null;
	var editRoleBean = null;	
	
	function setEditAccount(accountBean) {
		editAccountBean = accountBean;
	}
	function getEditAccount() {
		return editAccountBean;
	}
	
	function setEditRoleBean(roleBean) {
		editRoleBean = roleBean;
	}
	function getEditRoleBean() {
		return editRoleBean;
	}
	
	
    return {
    	aboutCompany: function(successCallback, failCallback){
        	$http({
    	        method: 'POST',
    	        url: './userinfo',
    	        headers: {
    	            'Content-Type': 'application/json; charset=UTF-8'
    	        },
            }).success(successCallback).error(failCallback);
        },
        aboutPermission: function(successCallback, failCallback){
        	$http({
    	        method: 'POST',
    	        url: './userpermission',
    	        headers: {
    	            'Content-Type': 'application/json; charset=UTF-8'
    	        },
            }).success(successCallback).error(failCallback);
        },
    	userLogin: function(user, successCallback, failCallback){
            $http({
    	        method: 'POST',
    	        url: './adminlogin',
    	        headers: {
    	        	'Content-Type': 'application/json; charset=UTF-8'
    	        },
    	        data: angular.toJson(user)
            }).success(successCallback).error(failCallback);
        },
        userLogout: function(successCallback, failCallback, data){
            $http({
    	        method: 'POST',
    	        url: './adminlogout',
    	        headers: {
    	        	'Content-Type': 'application/json; charset=UTF-8'
    	        },
    	        data: angular.toJson(data)
            }).success(successCallback).error(failCallback);
        },
        cueRequest: function(successCallback, failCallback, url, data){
        	$http({
    	        method: 'POST',
    	        url: url,
    	        headers: {
    	            'Content-Type': 'application/json; charset=UTF-8'
    	        },
    	        data: angular.toJson(data)
            }).success(function(data, status, headers, config){
            	if(data.code == 1)
            	{
            		successCallback(data, status, headers, config);
            	}	
            	else
            	{
            		if(data.code == -7) { 
            			alert(data.message);
            		} 
            		else { successCallback(data, status, headers, config); }	
            	}	
            }).error(failCallback);
        },
        cueRequestHeader: function(successCallback, failCallback, url, data,header){
        	$http({
    	        method: 'POST',
    	        url: url,
    	        headers: header,
    	        data: angular.toJson(data)
            }).success(successCallback).error(failCallback);
        },
        getRequest: function(successCallback, failCallback, url){
        	$http({
    	        method: 'GET',
    	        url: url,
            }).success(successCallback).error(failCallback);
        },
        cueGetFile: function(successCallback, failCallback, url, data){
        	$http({
    	        method: 'GET',
    	        url: url,
    	        headers: {
    	            'Content-Type': 'application/json; charset=UTF-8'
    	        },
    	        data: angular.toJson(data)
            }).success(successCallback).error(failCallback);
        },
        
        setEditAccount: setEditAccount,
        getEditAccount: getEditAccount,
        
        setEditRoleBean: setEditRoleBean,
        getEditRoleBean: getEditRoleBean,
    }
}]);