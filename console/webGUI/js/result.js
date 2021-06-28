window.onload = function () {
    server = 'http://10.11.163.179'
    let resultData = JSON.parse(window.localStorage.getItem('data'))
    console.log(resultData);

    class DrawElement{
        constructor() {
            this.resultHeader = document.querySelector('#resultHeader')
            this.downloadClient = document.querySelector('#downloadClient')
            this.downloadCase = document.querySelector('#downloadCase')
        }
        textTheResultHeader(){
            this.resultHeader.innerHTML = resultData.msg
            if (resultData.status == 599) {
                this.downloadCase.setAttribute('disabled', 'disabled')
                this.resultHeader.style.color = 'red'
            }
        }
    }
    let drawObj = new DrawElement()
    drawObj.textTheResultHeader()

    // case下载链接
    downloadUrl = server + resultData.downloadUrl
    downloadCaseA = document.getElementById('downloadCase')
    downloadCaseA.href = downloadUrl
}