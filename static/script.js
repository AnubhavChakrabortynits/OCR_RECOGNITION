document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('outimg').style.display = 'none'
    document.getElementById('loader').style.visibility = 'hidden'
    const canvas = document.getElementById('drawing-area');
    const canvasContext = canvas.getContext('2d');
    const clearButton = document.getElementById('clear-button');
    const saveButton = document.getElementById('save-button');
    const state = {
        mousedown: false
    };

    const baseLineWidth = 3;
    const devicePixelRatio = window.devicePixelRatio || 1;
    const lineWidth = baseLineWidth * devicePixelRatio*(7/9);
    const strokeStyle = '#333';

    canvas.addEventListener('mousedown', handleWritingStart);
    canvas.addEventListener('mousemove', handleWritingInProgress);
    canvas.addEventListener('mouseup', handleDrawingEnd);
    canvas.addEventListener('mouseout', handleDrawingEnd);

    canvas.addEventListener('touchstart', handleWritingStart);
    canvas.addEventListener('touchmove', handleWritingInProgress);
    canvas.addEventListener('touchend', handleDrawingEnd);

    clearButton.addEventListener('click', handleClearButtonClick);
    saveButton.addEventListener('click', handleSaveButtonClick);

    function handleWritingStart(event) {
        event.preventDefault();
        state.mousedown = true;
        const mousePos = getMousePositionOnCanvas(event);
        canvasContext.beginPath();
        canvasContext.moveTo(mousePos.x, mousePos.y);
        canvasContext.lineWidth = lineWidth;
        canvasContext.strokeStyle = strokeStyle;
        canvasContext.shadowColor = null;
        canvasContext.shadowBlur = 0;
    }

    function handleWritingInProgress(event) {
        event.preventDefault();
        if (state.mousedown) {
            const mousePos = getMousePositionOnCanvas(event);
            canvasContext.lineTo(mousePos.x, mousePos.y);
            canvasContext.stroke();
        }
    }

    function handleDrawingEnd(event) {
        event.preventDefault();
        if (state.mousedown) {
            canvasContext.shadowColor = null;
            canvasContext.shadowBlur = 0;
            canvasContext.stroke();
        }
        state.mousedown = false;
    }

    function handleClearButtonClick(event) {
        event.preventDefault();
        document.getElementById('outimg').style.display = 'none'
        document.getElementById('outtext').textContent = 'Your Output will be displayed here'
        clearCanvas();
    }

    function handleSaveButtonClick(event) {
        event.preventDefault();
        const dataUrl = canvas.toDataURL();
        sendDataToFlask(dataUrl);
    }

    function getMousePositionOnCanvas(event) {
        const clientX = event.clientX || (event.touches && event.touches[0].clientX);
        const clientY = event.clientY || (event.touches && event.touches[0].clientY);
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;   
        const scaleY = canvas.height / rect.height;
        const canvasX = (clientX - rect.left) * scaleX;
        const canvasY = (clientY - rect.top) * scaleY;
        return { x: canvasX, y: canvasY };
    }

    function clearCanvas() {
        canvasContext.clearRect(0, 0, canvas.width, canvas.height);
    }

   async function sendDataToFlask(dataUrl) {
        document.getElementById('loader').style.visibility = 'visible'
        const response = await fetch('/views', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ image: dataUrl })
        })

        const data = await response.json()
        const output_image = `data:image/png;base64,${data.output_image}`
        const output_string = data.output_string
        if(output_string){
        document.getElementById('outimg').style.display = "block"
        document.getElementById('outtext').textContent = output_string
        document.getElementById('outimg').src = output_image;
        }
        document.getElementById('loader').style.visibility = 'hidden'
    }
    

});
