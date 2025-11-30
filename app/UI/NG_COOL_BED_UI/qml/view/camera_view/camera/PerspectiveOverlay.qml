import QtQuick

Canvas {
    id: root
    property bool showOverlay: true
    property var shapes: []               // [{points, imageWidth, imageHeight, label}]
    property var visibilityMap: ({})      // label(lowercase) -> bool

    antialiasing: true

    onVisibleChanged: if (visible) requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()
    onShapesChanged: requestPaint()

    onPaint: {
        var ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)
        if (!root.showOverlay || !shapes || !shapes.length) return
        shapes.forEach((shape, idx) => {
            const pts = shape.points || []
            if (pts.length < 3) return
            const imgW = shape.imageWidth || 1
            const imgH = shape.imageHeight || 1
            const scale = Math.min(width / imgW, height / imgH)
            const offsetX = (width - imgW * scale) / 2
            const offsetY = (height - imgH * scale) / 2
            const key = (shape.label || "").toLowerCase()
            if (visibilityMap && visibilityMap[key] === false) return
            ctx.beginPath()
            pts.forEach((p, i) => {
                const x = p[0] * scale + offsetX
                const y = p[1] * scale + offsetY
                if (i === 0) ctx.moveTo(x, y)
                else ctx.lineTo(x, y)
            })
            ctx.closePath()
            const colors = ["#4caf50", "#03a9f4", "#ffeb3b", "#e91e63", "#9c27b0"]
            const color = colors[idx % colors.length]
            ctx.strokeStyle = color
            ctx.fillStyle = color + "33"
            ctx.lineWidth = 2
            ctx.fill()
            ctx.stroke()
        })
    }
}
