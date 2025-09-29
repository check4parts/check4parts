<script lang="ts">
	import { goto, preloadData } from '$app/navigation';
	import { page } from '$app/state';
	import { Tabs } from '@skeletonlabs/skeleton-svelte';
	import { onMount } from 'svelte';

	let { children } = $props();
	let group = $state<string>();

	$effect(() => {
		const basePath = '/home/settings/suppliers';
		const newPath = `${basePath}/${group}`;

    if (group && !page.url.pathname.includes(newPath)) {
			goto(newPath);
		}
	});

	onMount(() => {
		const pathSegments = page.url.pathname.split('/');
		const lastSegment = pathSegments[pathSegments.length - 1];

		if (lastSegment === 'api' || lastSegment === 'loaded') {
			group = lastSegment;
		} else {
			group = 'api';
		}
	});
</script>

<main class="grid h-full grid-rows-[auto_1fr]">
	<header>
		<div class="flex items-center justify-between">
			<h2 class="h3">Постачальники</h2>
		</div>
		<section id="tabs" class="overflow-hidden">
			<Tabs
				value={group}
				onValueChange={(e) => {
					group = e.value;
				}}
			>
				{#snippet list()}
					<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="api"
						><p onmousemove={() => preloadData('/home/settings/suppliers/api')}>
							API
						</p></Tabs.Control
					>
					<Tabs.Control stateActive="font-normal !border-b-3 !border-primary-950" value="loaded"
						><p onmousemove={() => preloadData('/home/settings/suppliers/loaded')}>Прайс-лист</p>
					</Tabs.Control>
				{/snippet}
			</Tabs>
		</section>
	</header>
  <section>
    {@render children()}
  </section>
</main>
