const canvas = document.getElementById("heart");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let hearts = [];

class Heart {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = canvas.height + Math.random() * 100;
        this.size = Math.random() * 20 + 10;
        this.speed = Math.random() * 1 + 0.5;
        this.alpha = Math.random();
    }

    draw() {
        ctx.globalAlpha = this.alpha;
        ctx.fillStyle = "#ff4d6d";
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.bezierCurveTo(
            this.x - this.size,
            this.y - this.size,
            this.x - this.size * 2,
            this.y + this.size / 2,
            this.x,
            this.y + this.size
        );
        ctx.bezierCurveTo(
            this.x + this.size * 2,
            this.y + this.size / 2,
            this.x + this.size,
            this.y - this.size,
            this.x,
            this.y
        );
        ctx.fill();
    }

    update() {
        this.y -= this.speed;
        if (this.y < -50) {
            this.y = canvas.height + 50;
            this.x = Math.random() * canvas.width;
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    hearts.forEach(h => {
        h.update();
        h.draw();
    });
    requestAnimationFrame(animate);
}

for (let i = 0; i < 50; i++) {
    hearts.push(new Heart());
}

animate();
