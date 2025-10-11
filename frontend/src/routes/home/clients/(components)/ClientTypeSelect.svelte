<script lang="ts">
	type Item = {
		id: string;
		name: string;
	};

	type Props = {
		items: Item[];
		selectedIds?: string[];
		label?: string;
		onchange?: (selected: string[]) => void;
	};

	let { items, selectedIds = $bindable([]), label = 'Фільтр' }: Props = $props();

	let isOpen = $state(false);

	let isAllSelected = $derived(selectedIds.length === items.length);
	let isIndeterminate = $derived(selectedIds.length > 0 && selectedIds.length < items.length);

	function toggleDropdown() {
		isOpen = !isOpen;
	}

	function selectAll() {
		if (isAllSelected) {
			selectedIds = [];
		} else {
			selectedIds = items.map((item) => item.id);
		}
	}

	function removeItem(id: string) {
		selectedIds = selectedIds.filter((itemId) => itemId !== id);
	}

	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.dropdown-container')) {
			isOpen = false;
		}
	}

	// Отримання назви елемента за ID
	function getItemName(id: string): string {
		return items.find((item) => item.id === id)?.name ?? '';
	}
</script>

<svelte:document onclick={handleClickOutside} />

<div class="dropdown-container relative inline-block">
	<button
		type="button"
		onclick={toggleDropdown}
		class="border-primary-950 hover:bg-primary-50 border-1 flex min-w-[200px] items-center justify-between gap-2 rounded-lg bg-white px-4 py-2 transition-colors"
	>
		<span class="font-medium">{label}</span>
		{#if selectedIds.length > 0}
			<span class="badge preset-filled-primary-950-50 rounded-full">{selectedIds.length}</span>
		{/if}
		<svg
			class="h-4 w-4 transition-transform duration-200"
			class:rotate-180={isOpen}
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	{#if isOpen}
		<div
			class="border-primary-950 absolute left-0 z-50 min-w-full rounded-lg border-2 bg-white shadow-lg"
		>
			<!-- Опція "Вибрати все" -->
			<div class="border-primary-950 border-b-2 p-2">
				<label
					class="hover:bg-primary-50 flex cursor-pointer items-center gap-2 rounded px-2 py-1.5"
				>
					<input
						type="checkbox"
						checked={isAllSelected}
						indeterminate={isIndeterminate}
						onchange={selectAll}
						class="h-4 w-4 cursor-pointer"
					/>
					<span class="font-semibold">Вибрати все</span>
				</label>
			</div>

			<!-- Список елементів -->
			<div class="max-h-[300px] overflow-y-auto p-2">
				{#each items as item (item.id)}
					<label
						class="hover:bg-primary-50 flex cursor-pointer items-center gap-2 rounded px-2 py-1.5"
					>
						<input
							type="checkbox"
							value={item.id}
							bind:group={selectedIds}
							class="h-4 w-4 cursor-pointer"
						/>
						<span>{item.name}</span>
					</label>
				{/each}
			</div>
		</div>
	{/if}
</div>
