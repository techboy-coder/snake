import type { Writable } from 'svelte/store';
export function get__store<T>(store: Writable<T>): T | undefined {
	let $val;
	store.subscribe(($) => ($val = $))();
	return $val;
}
