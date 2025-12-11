export function showLoading() {
    document.getElementById("loading-overlay").style.display = "flex";
}

export function hideLoading() {
    document.getElementById("loading-overlay").style.display = "none";
}

export function formatList(arr) {
    if (!arr || arr.length === 0) return "None";

    if (arr.length > 10) {
        return arr.slice(0, 10).join(", ") + ` ... (+${arr.length - 10} more)`;
    }
    return arr.join(", ");
}

export function getRandomColor(seed, alpha=1){
    const colors = [
        [102, 126, 234],
        [118, 75, 162],
        [236, 72, 153],
        [59, 130, 246],
        [16, 185, 129],
        [245, 158, 11],
    ];
    const color = colors[seed % colors.length];
    return `rgba(${color[0]},${color[1]},${color[2]},${alpha})`;
}