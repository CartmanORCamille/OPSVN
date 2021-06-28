window.onload = function(){
    /*
        1. 读取html表单控件
        2. 读取json文件
        3. 写入json文件
        4. 启动python文件
    
    */

    // 读取html表单值
    class GetHTMLValues{
        constructor() {
            this.versionRange = []
            this.dateRange = []
            this.defectBehavior = NaN
            this.gamePlay = NaN
            this.needCheckPath = NaN
            this.binPath = NaN
        }
        
        getValues(){
            /*
                1. 范围 - 版本/时间范围
                2. 游戏缺陷行为
                3. 游戏内操作
                4. 游戏目录 - 查验目录/bin64
             */
            this.versionRange = [
                document.getElementsByName('versionForBegin')[0].value,
                document.getElementsByName('versionForEnd')[0].value,
            ]
            this.dateRange = [
                document.getElementsByName('timeForBegin')[0].value,
                document.getElementsByName('timeForEnd')[0].value,
            ]

            this.defectBehavior = this.getRadioValue(document.getElementsByName('defectBehavior'))

            this.gamePlay = this.getRadioValue(document.getElementsByName('gamePlay'))

            this.needCheckPath = document.getElementsByName('needCheckPath')[0].value
            this.binPath = document.getElementsByName('binPath')[0].value
            
            let info = {
                'versionRange': this.versionRange,
                'dateRange': this.dateRange,
                'defectBehavior': this.defectBehavior,
                'gamePlay': this.gamePlay,
                'needCheckPath': this.needCheckPath,
                'binPath': this.binPath,
            }
            return info
        }

        getRadioValue(radioObj){
            let data = []
            for (let i = 0; i < radioObj.length; i++) {
                const element = radioObj[i];
                if (element.checked) {
                    data.push(element.value)
                }
            }
            return data[0]
        }
        
    }
    let getValueObj = new GetHTMLValues()
    
    // AJAX
    let IVADUrl = 'http://10.11.163.179/api/infoVerificationAndDownload/'
    let localTestIVADUrl = 'http://127.0.0.1:8000/api/infoVerificationAndDownload/'
    
    let submitBtn = document.getElementById('submit')
    submitBtn.onclick = function () {
        let IVADData = getValueObj.getValues()
        fetch(IVADUrl, {
            method: 'POST',
            body: JSON.stringify(IVADData),
            headers: new Headers({
                'Content-Type': 'application/json'
            })
        }).then(function (result) {
            if (result.ok) {
                return result.json()
            }
        }).then(function (result) {
            
            if (result.status == 200 || result.status == 599) {
                // 正常提交
                location.assign('..\\html\\result.html')
                window.localStorage.setItem('data', JSON.stringify(result))
            }else{
                // 其他错误
            }
        })
    }


    // 获取两个范围ID -> input disabled逻辑
    let versionCheckBox = document.getElementById('versionCheck')
    let dateCheckBox = document.getElementById('dateCheck')

    let versionInput = document.querySelectorAll('.versionRange > input')
    let dateInput = document.querySelectorAll('.dateRange > input')

    versionCheckBox.onclick = function () {
        for (let k = 0; k < versionInput.length; k++) {
            const element = versionInput[k];
            element.removeAttribute('disabled', 'disabled')
        }
        for (let i = 0; i < dateInput.length; i++) {
            const element = dateInput[i];
            element.setAttribute('disabled', 'disabled')
        }
    }

    dateCheckBox.onclick = function () {
        for (let k = 0; k < dateInput.length; k++) {
            const element = dateInput[k];
            element.removeAttribute('disabled', 'disabled')
        }
        for (let i = 0; i < versionInput.length; i++) {
            const element = versionInput[i];
            element.setAttribute('disabled', 'disabled')
        }
    }
}