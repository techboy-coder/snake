<script lang="ts">
	import { onMount } from 'svelte';

	import Welcome from '../pages/welcome.svelte';
	import { Connection, hasJoined, ProtData, type Protocol, PlayerName } from '../script/connection';
	import { Draw } from '../script/draw';

	onMount(() => {
		window.addEventListener('keypress', handleMovement);
		window.addEventListener('keydown', handleMovement);
	});

	let draw = new Draw();
	let protdata: Protocol;
	let score: Number = 0;
	ProtData.subscribe((d) => {
		protdata = d;
		if (d && d.Player && d.Player.Score) {
			score = d.Player.Score;
		}
	});
	function sleep(time: number) {
		return new Promise((resolve) => setTimeout(resolve, time));
	}
	hasJoined.subscribe((d) => {
		if (d) {
			sleep(500).then(() => {
				draw = new Draw();
			});
		}
	});
	let handleJoin = (protdata: Protocol) => {
		if ($hasJoined) {
			draw.clear();
			if (protdata && protdata.Field) {
				draw.render(protdata.Field);
			}
		}
	};
	$: handleJoin(protdata);
	const handleMovement = (e: KeyboardEvent) => {
		if ($hasJoined) {
			switch (e.key) {
				case 'a':
					// left
					Connection.turn(0);
					break;
				case 'd':
					// right
					Connection.turn(1);
					break;
				case 'w':
					// up
					Connection.turn(2);
					break;
				case 's':
					// down
					Connection.turn(3);
					break;
			}
		}
	};
	type SimpleSnake = {
		Name: string;
		Score: number;
	};
	type Leaderboard = {
		Leaderboard: SimpleSnake[];
	};
	let leaderboard: Leaderboard;
	let updateleaderboard = async () => {
		let res = await fetch('http://localhost:8080/leaderboard');
		leaderboard = await res.json();
	};
	updateleaderboard();
	setInterval(updateleaderboard, 1000);
	$: console.log('lb', JSON.stringify(leaderboard), leaderboard);
</script>

<div class="h-screen w-screen bg-white text-black">
	{#if !$hasJoined}
		<!-- {#if leaderboard && leaderboard.Leaderboard}
			<div class="relative">
				<div
					class="absolute text-black text-xl font-mono right-14 top-8 bg-red border-black border-4 py-5 px-4 rounded-md"
				>
					<div class="">Total Snakes: {leaderboard.Leaderboard.length}</div>
					<br />
					<div class="flex flex-col">
						<span class="font-bold">Leaderboard</span>
						{#each leaderboard.Leaderboard.splice(0, 10) as snek}
							<span>{snek.Name} - {snek.Score}</span>
						{/each}
					</div>
				</div>
			</div>
		{/if} -->
		<Welcome />
	{/if}
	<!-- {:else} -->
	{#if $hasJoined}
		<div class="h-full w-full overflow-hidden bg-white">
			<div class="relative">
				<div
					class="absolute text-black text-xl font-mono right-14 top-8 bg-red border-black border-4 py-5 px-4 rounded-md"
				>
					<span class="font-bold">Name: {$PlayerName}</span> <br />
					<div class="italic" />
					<div class="">
						Score: {score}
					</div>
					<div class="">Total Snakes: {leaderboard.Leaderboard.length}</div>
					<br />
					<div class="flex flex-col">
						<span class="font-bold">Leaderboard</span>
						{#each leaderboard.Leaderboard.splice(0, 10) as snek}
							<span>{snek.Name} - {snek.Score}</span>
						{/each}
					</div>
				</div>
			</div>
			<canvas id="gamewindow" style="overflow: hidden" />
		</div>
	{/if}
</div>
