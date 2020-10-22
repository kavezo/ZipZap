// ビルド時に書き換わる
window.resDir = "";
window.isDebug = false;// 本番環境でfalseになる
var fileTimeStamp = {};
var deleteConfirms = [{"confirmFileNames":["image_native/bg/quest/bg_quest_11024.png.aaa","image_native/bg/quest/bg_quest_11024.png.aab","image_native/bg/quest/bg_quest_12062.png.aaa","image_native/bg/quest/bg_quest_12062.png.aab"],"jsonFilePath":"json/system/deleteResource20180319.json"},{"confirmFileNames":["sound_native/fullvoice/section_101801/vo_full_101801-10-10_hca.hca","sound_native/fullvoice/section_101801/vo_full_101801-10-11_hca.hca","sound_native/fullvoice/section_101801/vo_full_101801-10-12_hca.hca","sound_native/fullvoice/section_101801/vo_full_101801-10-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101801.json"},{"confirmFileNames":["sound_native/fullvoice/section_101802/vo_full_101802-1-10_hca.hca","sound_native/fullvoice/section_101802/vo_full_101802-1-11_hca.hca","sound_native/fullvoice/section_101802/vo_full_101802-1-12_hca.hca","sound_native/fullvoice/section_101802/vo_full_101802-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101802.json"},{"confirmFileNames":["sound_native/fullvoice/section_101803/vo_full_101803-1-10_hca.hca","sound_native/fullvoice/section_101803/vo_full_101803-1-11_hca.hca","sound_native/fullvoice/section_101803/vo_full_101803-1-12_hca.hca","sound_native/fullvoice/section_101803/vo_full_101803-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101803.json"},{"confirmFileNames":["sound_native/fullvoice/section_101804/vo_full_101804-1-10_hca.hca","sound_native/fullvoice/section_101804/vo_full_101804-1-11_hca.hca","sound_native/fullvoice/section_101804/vo_full_101804-1-12_hca.hca","sound_native/fullvoice/section_101804/vo_full_101804-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101804.json"},{"confirmFileNames":["sound_native/fullvoice/section_101805/vo_full_101805-1-10_hca.hca","sound_native/fullvoice/section_101805/vo_full_101805-1-11_hca.hca","sound_native/fullvoice/section_101805/vo_full_101805-1-12_hca.hca","sound_native/fullvoice/section_101805/vo_full_101805-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101805.json"},{"confirmFileNames":["sound_native/fullvoice/section_101806/vo_full_101806-1-10_hca.hca","sound_native/fullvoice/section_101806/vo_full_101806-1-11_hca.hca","sound_native/fullvoice/section_101806/vo_full_101806-1-12_hca.hca","sound_native/fullvoice/section_101806/vo_full_101806-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101806.json"},{"confirmFileNames":["sound_native/fullvoice/section_101807/vo_full_101807-1-11_hca.hca","sound_native/fullvoice/section_101807/vo_full_101807-1-12_hca.hca","sound_native/fullvoice/section_101807/vo_full_101807-1-13_hca.hca","sound_native/fullvoice/section_101807/vo_full_101807-1-14_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101807.json"},{"confirmFileNames":["sound_native/fullvoice/section_101808/vo_full_101808-1-10_hca.hca","sound_native/fullvoice/section_101808/vo_full_101808-1-11_hca.hca","sound_native/fullvoice/section_101808/vo_full_101808-1-12_hca.hca","sound_native/fullvoice/section_101808/vo_full_101808-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101808.json"},{"confirmFileNames":["sound_native/fullvoice/section_101809/vo_full_101809-1-10_hca.hca","sound_native/fullvoice/section_101809/vo_full_101809-1-11_hca.hca","sound_native/fullvoice/section_101809/vo_full_101809-1-12_hca.hca","sound_native/fullvoice/section_101809/vo_full_101809-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101809.json"},{"confirmFileNames":["sound_native/fullvoice/section_101810/vo_full_101810-1-10_hca.hca","sound_native/fullvoice/section_101810/vo_full_101810-1-11_hca.hca","sound_native/fullvoice/section_101810/vo_full_101810-1-12_hca.hca","sound_native/fullvoice/section_101810/vo_full_101810-1-13_hca.hca"],"jsonFilePath":"json/system/delete_asset_section_101810.json"}];

window.hotReload = function(mypageFetch){
	// console.log(pathWhiteList);
	require.undef("releaseInfo");
	require(["releaseInfo"],function(){
		// console.log("window.breforeReleaseTime",window.breforeReleaseTime);
		// console.log("releaseTime",releaseTime);
		if(!window.breforeReleaseTime || window.breforeReleaseTime !== releaseTime){
			window.breforeReleaseTime = releaseTime;
	require.undef("replacement");
			require(["replacement"],function(){
				// console.log("run hotreload replacement")
	_.each(pathWhiteList,function(content,key) {
		require.undef(key);
	});
	_.each(fileTimeStamp,function(content,key) {
		if(key.indexOf("css/") !== -1 || key.indexOf("template/") !== -1) {
			require.undef("text!"+key);
			// console.log("text!"+key);
					}
				});

				mypageFetch();
			});
		}else{
			mypageFetch();
		}
	});
};

window.deleteAssetArr = function(){
	return deleteConfirms;
};
