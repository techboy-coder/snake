<script>
	import { Connection, hasJoined, PlayerName, isConnected } from '../script/connection';

	// import { name } from '../script/store';

	const handleSubmit = () => {
		Connection.join();
		hasJoined.set(true);
	};
</script>

<div class="h-5/6 flex flex-col justify-center">
	<div class="w-full flex justify-center">
		<div
			class="h-full flex flex-col justify-center items-center space-y-5 ease-in-out duration-100"
		>
			<h1 class="font-bold text-8xl uppercase">Snake</h1>
			<form on:submit|preventDefault={handleSubmit} class="">
				<input
					type="text"
					bind:value={$PlayerName}
					placeholder="nickname"
					class="px-4 font-mono font-bold text-3xl py-2
                    text-black outline-none border-light focus-within:border-dark border-4 placeholder-light ease-in-out duration-100"
				/>
				<button type="submit" class=" text-black">
					<div
						class="bg-red px-10 font-mono font-bold text-3xl py-2 border-4 border-dark flex hover:bg-dark hover:text-white"
					>
						<div class="z-20 w-full h-full">Join</div>
					</div>
				</button>
			</form>
			<div class="text-black font-mono font-bold text-2xl">
				{#if !$isConnected}
					<div class="">Please wait, connecting to server...</div>
				{:else}
					<div class="">Press 'Join' to play game</div>
				{/if}
			</div>
		</div>
	</div>
</div>
