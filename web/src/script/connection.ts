import { browser } from '$app/env';
import WebSocket from 'isomorphic-ws';
import { writable, type Writable } from 'svelte/store';
import { get__store } from './helpers';

type Stats = {
	SnakeAmount?: Number;
};
type Player = {
	ViewDistance?: Number;
	Score?: Number;
	Name?: string;
	Direction?: Number;
};

export type Protocol = {
	Job?: string;
	Stats?: Stats;
	Player?: Player;
	Field?: Number[][];
};

export let ProtData: Writable<Protocol> = writable();
export let isConnected: Writable<boolean> = writable(false);
export let hasJoined: Writable<boolean> = writable(false);
export let PlayerName: Writable<string> = writable('');
// export let ViewDistance = 150;
export let ViewDistance = 200;

export class Conn {
	ws: WebSocket;
	constructor() {
		if (browser) {
			this.ws = new WebSocket('ws://localhost:8080/ws');
			this.ws.onopen = function open() {
				console.log('connected');
				isConnected.set(true);
			};

			this.ws.onclose = function close() {
				isConnected.set(false);
				console.log('disconnected');
				this.ws = new WebSocket('ws://localhost:8080/ws');
			};

			this.ws.onmessage = (data: MessageEvent) => {
				let prot: Protocol = JSON.parse(data.data);
				ProtData.set(prot);
				if (prot.Job == 'dead') {
					hasJoined.set(false);
				}
			};
		}
	}
	join() {
		let name = get__store(PlayerName);
		if (name == undefined || name.length < 1) {
			name = 'anon';
		}
		let p: Protocol = {
			Job: 'join',
			Player: {
				ViewDistance: ViewDistance,
				Name: name
			}
		};
		this.ws.send(JSON.stringify(p));
		// console.log('joined', JSON.stringify(p));
		hasJoined.set(true);
	}
	turn(direction: number) {
		let p: Protocol = {
			Job: 'turn',
			Player: {
				Direction: direction
			}
		};
		this.ws.send(JSON.stringify(p));
		// console.log('joined', JSON.stringify(p));
		hasJoined.set(true);
	}
}

export let Connection = new Conn();
