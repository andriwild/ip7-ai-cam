console.log('roi.js loaded');

const imgContainer = document.getElementById('imgContainer');
const theImage     = document.getElementById('theImage');
const roiOverlay   = document.getElementById('roiOverlay');

const startXSpan   = document.getElementById('startX');
const startYSpan   = document.getElementById('startY');
const endXSpan     = document.getElementById('endX');
const endYSpan     = document.getElementById('endY');

const roiXSpan     = document.getElementById('roiX');
const roiYSpan     = document.getElementById('roiY');
const roiWSpan     = document.getElementById('roiW');
const roiHSpan     = document.getElementById('roiH');

let startX, startY;
let isDrawing = false;

imgContainer.addEventListener('mousedown', (e) => {
    e.preventDefault();
    e.stopPropagation();
    isDrawing = true;

    const rect = theImage.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;

    roiOverlay.style.left = `${startX}px`;
    roiOverlay.style.top = `${startY}px`;
    roiOverlay.style.width = `0px`;
    roiOverlay.style.height = `0px`;

    startXSpan.textContent = startX.toFixed(2);
    startYSpan.textContent = startY.toFixed(2);
});

imgContainer.addEventListener('mousemove', (e) => {

    e.preventDefault();
    e.stopPropagation();
    if (!isDrawing) return;

    const rect = theImage.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;

    const width = currentX - startX;
    const height = currentY - startY;

    roiOverlay.style.width = `${Math.abs(width)}px`;
    roiOverlay.style.height = `${Math.abs(height)}px`;

    roiOverlay.style.left = `${Math.min(startX, currentX)}px`;
    roiOverlay.style.top = `${Math.min(startY, currentY)}px`;

    endXSpan.textContent = currentX.toFixed(2);
    endYSpan.textContent = currentY.toFixed(2);
});

imgContainer.addEventListener('mouseup', (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isDrawing) return;
    isDrawing = false;

    const rect = theImage.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;

    const roiX = Math.min(startX, endX);
    const roiY = Math.min(startY, endY);
    const roiW = Math.abs(endX - startX);
    const roiH = Math.abs(endY - startY);

    roiXSpan.textContent = roiX.toFixed(2);
    roiYSpan.textContent = roiY.toFixed(2);
    roiWSpan.textContent = roiW.toFixed(2);
    roiHSpan.textContent = roiH.toFixed(2);
});
