import { browser } from '$app/env';
import { ProtData, ViewDistance, type Protocol } from '../script/connection';
import { get__store } from './helpers';

export class Draw {
	protdata: Protocol | undefined;
	canvas: HTMLCanvasElement | undefined;
	ctx: CanvasRenderingContext2D | undefined;
	scaler: number;
	constructor() {
		this.protdata = get__store(ProtData);
		// this.scaler = 10;
		this.scaler = 30;
		if (browser) {
			this.canvas = <HTMLCanvasElement>document.getElementById('gamewindow');
			if (this.canvas) {
				this.resize();
				window.addEventListener('resize', this.resize);
				this.ctx = <CanvasRenderingContext2D>this.canvas.getContext('2d');
				this.clear();
			}
		}
	}
	resize() {
		if (browser && this.canvas) {
			this.canvas.width = window.innerWidth;
			this.canvas.height = window.innerHeight;
		}
	}
	clear() {
		if (browser && this.canvas && this.ctx) {
			this.ctx.fillStyle = '#3a3a3a';
			this.ctx.strokeStyle = '#3a3a3a';
			this.ctx.fillRect(
				-this.canvas.width * 2,
				-this.canvas.height * 2,
				this.canvas.width * 4,
				this.canvas.height * 4
			);
		}
	}
	render(field: Number[][]) {
		if (browser && this.canvas && this.ctx) {
			this.ctx.save();
			this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
			for (let i = 0; i < field.length; i++) {
				const row = field[i];
				for (let j = 0; j < row.length; j++) {
					const element = row[j];
					let x = j - ViewDistance;
					let y = i - ViewDistance;
					// if (element == -1) {
					// 	this.ctx.fillStyle = '#1e1e1e';
					// 	this.ctx.strokeStyle = '#1e1e1e';
					// 	this.ctx.fillRect(x * this.scaler, y * this.scaler, this.scaler, this.scaler);
					// }
					if (element == 0) {
						this.ctx.fillStyle = '#cdcdcd';
						this.ctx.strokeStyle = '#cdcdcd';
						this.ctx.fillRect(x * this.scaler, y * this.scaler, this.scaler, this.scaler);
						this.ctx.strokeRect(x * this.scaler, y * this.scaler, this.scaler, this.scaler);
					}
					if (element == 1) {
						// this.ctx.fillStyle = '#ff5558';
						this.ctx.fillStyle = '#bbbbbb';
						this.ctx.strokeStyle = '#cdcdcd';
						let d = 10;
						this.ctx.lineWidth = d + 1;
						this.ctx.strokeRect(
							x * this.scaler + d / 2,
							y * this.scaler + d / 2,
							this.scaler - d,
							this.scaler - d
						);
						this.ctx.fillRect(
							x * this.scaler + d / 2,
							y * this.scaler + d / 2,
							this.scaler - d,
							this.scaler - d
						);
						this.ctx.lineWidth = 1;
					}
					if (element == 2) {
						this.ctx.fillStyle = '#ff5558';
						this.ctx.strokeStyle = '#ff5558';
						this.ctx.fillRect(x * this.scaler, y * this.scaler, this.scaler, this.scaler);
						this.ctx.strokeRect(x * this.scaler, y * this.scaler, this.scaler, this.scaler);
					}
				}
			}
			this.ctx.restore();
		}
	}
}
