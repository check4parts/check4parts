<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import toast from 'svelte-french-toast';

	let { data } = $props();
	let { clients } = $derived(data);

	const isSuccess = page.url.searchParams.has('success');
	$effect(() => {
		if (isSuccess) {
			toast.success('Клієнт успішно додано');
			goto('/home/clients', { replaceState: true, noScroll: true, keepFocus: true });
		}
	});
</script>

{#snippet noClientsMessage()}
	<div class="flex h-full w-full flex-col items-center justify-center">
		<h3 class="h5">Тут поки що порожньо.</h3>
		<p>Додайте першого клієнта, щоб розпочати роботу.</p>
	</div>
{/snippet}

<header class="flex items-center justify-between">
	<h2 class="h3">Клієнти</h2>
	<a class="btn preset-filled-primary-950-50" href="/home/clients/add">Додати клієнта</a>
</header>

{#if clients.length > 0}
	...
{:else}
	<section class="h-2/3">
		{@render noClientsMessage()}
	</section>
{/if}
