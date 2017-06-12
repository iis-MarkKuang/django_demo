var errorMessage = {
	username: "用户名",
	password: "密码",
	password_repeat: "确认密码",
	phone: "手机号"
}
function  validateForms(formEelem) {
	var formParamsObj = {};
	var formSegmentArray = $(formEelem).serialize().split("&");
	var validate = true;
	for(var i = 0, length = formSegmentArray.length; i < length; i++){
		var currentParam = formSegmentArray[i].split("=");
		formParamsObj[currentParam[0]] = currentParam[1];
	}
	
	$.each(formParamsObj,function(key, value){
		if(!value) {
		  validate = false;
		  $(".error-tip").text("*" + errorMessage[key] + "不能为空");
		  return false;
		}

		if(key == "phone" && !validateMobileFormat(value)){
			validate = false;
		  $(".error-tip").text("*" + errorMessage[key] + "格式不正确");
		  return false;
		}
	})

	return validate;
}

function validateMobileFormat(mobile){
	if (!mobile.match(/^0?(13[0-9]|15[0-9]|18[0-9]|14[0-9]|17[0-9])[0-9]{8}$/)) {
    return false;
  }
  return true;
}