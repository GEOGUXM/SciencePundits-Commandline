window.addEventListener("DOMContentLoaded",function(){KangoAPI.getBackgroundPage=function(){return window.kango.getBackgroundPage()};KangoAPI.closeWindow=function(){window.__optionsPageMode?kango.ui.optionsPage.close():kango.ui.browserButton.closePopup()};KangoAPI.resizeWindow=function(a,b){window.__optionsPageMode||kango.ui.browserButton.resizePopup(a,b)};KangoAPI.fireReady()},!1);