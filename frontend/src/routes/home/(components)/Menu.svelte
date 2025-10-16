<script lang="ts">
	import { goto } from '$app/navigation';
	import { slide } from 'svelte/transition';

	let { page }: { page: string } = $props();

	let subMenuOpen = $state<string>();
</script>

{#snippet menuItem(
	pageValue: string,
	pageTitle: string,
	pageIcon: string,
	selectedPageIcon: string,
	link: string | undefined = undefined
)}
	<button
		class:font-bold={page === pageValue}
		class="flex items-center gap-2 text-xl"
		onclick={() => {
			if (subMenuOpen === pageValue) {
				subMenuOpen = undefined;
				return;
			}
			subMenuOpen = pageValue;
			if (link) {
				goto(link);
			}
		}}
	>
		<img src={page === pageValue ? selectedPageIcon : pageIcon} alt={pageValue} class="size-6" />
		{pageTitle}
	</button>
{/snippet}

{#snippet subMenu(
	pageValue: string,
	root: string = '/home',
	subPages: { page: string; title: string }[]
)}
	{#if page === pageValue || subMenuOpen === pageValue}
		<ul class="pl-9" transition:slide={{ duration: 200 }}>
			{#each subPages as subPage (subPage.page)}
				<li>
					<a href="{root}/{pageValue}/{subPage.page}" class="anchor">{subPage.title}</a>
				</li>
			{/each}
		</ul>
	{/if}
{/snippet}

<div class="flex flex-col gap-2">
	<ul>
		<li>
			{@render menuItem(
				'clients',
				'Клієнти',
				'/clients-icon.svg',
				'/clients-icon-selected.svg',
				'/home/clients'
			)}
		</li>
		<li>
			{@render menuItem(
				'settings',
				'Налаштування',
				'/settings-icon.svg',
				'/settings-icon-selected.svg'
			)}
			{@render subMenu('settings', undefined, [
				{ page: 'trading-points', title: 'Торгівельні точки' },
				{ page: 'users', title: 'Користувачі' },
				{ page: 'suppliers', title: 'Постачальники' }
			])}
		</li>
	</ul>
</div>
