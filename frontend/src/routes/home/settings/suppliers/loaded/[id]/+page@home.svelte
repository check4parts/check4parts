<script>
	let { data } = $props();
	let { price, price_history, warehouses, count, reference_count } = $derived(data);
</script>

<main class="grid h-full grid-rows-[auto_1fr] gap-2">
	<section>
		<div class="border-primary-950 overflow-hidden rounded-xl border-2">
			<div class="border-primary-950 p-4">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<h3 class="text-primary-950 text-lg font-bold">Деталі імпорту прайсу</h3>
						<div class="mt-2 space-y-1">
							<p class="text-sm">
								<span class="text-primary-900 font-medium">Історичне ID:</span>
								<span class="font-mono">{price_history.id}</span>
							</p>
							{#if price_history.loaded_prices}
								<p class="text-sm">
									<span class="text-primary-900 font-medium">ID імпорту:</span>
									<span class="font-mono">{price_history.loaded_prices?.id}</span>
								</p>
								<p class="text-sm">
									<span class="text-primary-900 font-medium">HASH імпорту:</span>
									<span class="font-mono">{price_history.loaded_prices?.hash}</span>
								</p>
							{/if}
							<p class="text-sm">
								<span class="text-primary-900 font-medium">Дата:</span>
								{new Date(price_history.created_at).toLocaleDateString('uk-UA', {
									year: 'numeric',
									month: '2-digit',
									day: '2-digit',
									hour: '2-digit',
									minute: '2-digit'
								})}
							</p>
							<p class="text-sm">
								<span class="text-primary-900 font-medium">Постачальник:</span>
								{price_history.providers?.name || 'Не вказано'}
								{#if price_history.providers?.short_name}
									<span class="ml-1 text-xs">({price_history.providers.short_name})</span>
								{/if}
							</p>
							{#if price_history.status === 'actual' || price_history.status === 'cloned'}
								<p class="text-sm">
									<span class="text-primary-900 font-medium">Статус:</span>
									<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
										Актуальний
										{#if price_history.status === 'cloned'}
											({reference_count})
										{/if}
									</span>
								</p>
								<p class="text-sm">
									<span class="text-primary-900 font-medium">Кількість:</span>
									{count} рядків
								</p>
							{:else if price_history.status === 'deleted'}
								<p class="text-sm">
									<span class="text-primary-900 font-medium">Статус:</span>
									<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800">
										Видалено
									</span>
								</p>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<section class="overflow-hidden flex flex-col">
		{#await price}
			<p class="text-center text-gray-500">Завантаження попереднього перегялду прайсу...</p>
		{:then prices}
			<h4 class="text-lg font-bold">Попередній перегляд</h4>
			{@const localWarehouses = warehouses.filter((w) => {
				return Object.keys(prices[1]?.rests).includes(w.id);
			})}
			{#if price_history.status !== 'deleted'}
				<div class="border-primary-950 overflow-hidden rounded-xl border-2">
					<div class="max-h-full overflow-y-auto">
						<table class="table border-collapse">
							<thead class="bg-primary-950 sticky top-0 z-10">
								<tr class="text-primary-50">
									<th class="p-2">Бренд</th>
									<th class="p-2">Артикул</th>
									<th class="p-2">Опис</th>
									<th class="p-2">Ціна</th>
									{#each localWarehouses as warehouse}
										<th class="p-2">
											{warehouse.name}
											{#if warehouse.short_name}
												<span class="ml-1 text-xs">({warehouse.short_name})</span>
											{/if}
										</th>
									{/each}
								</tr>
							</thead>
							<tbody class="!divide-primary-950 !divide-y-2 overflow-y-auto">
								{#each prices as item (item.id)}
									<tr class="divide-primary-950 hover:bg-primary-50 group w-full divide-x-2">
										<td class="p-2 font-medium">{item.brand}</td>
										<td class="p-2 font-mono">{item.article}</td>
										<td class="p-2">{item.description}</td>
										<td class="p-2 font-medium">
											{new Intl.NumberFormat('uk-UA', {
												style: 'currency',
												currency: 'UAH',
												minimumFractionDigits: 2
											}).format(item.price)}
										</td>

										{#each localWarehouses as warehouse}
											<td class="p-2 text-center">
												{#if item.rests[warehouse.id] && item.rests[warehouse.id] !== '0'}
													<span class="rounded-full bg-green-100 px-2 py-1 text-xs text-green-800">
														{item.rests[warehouse.id]}
													</span>
												{:else}
													<span class="rounded-full bg-red-100 px-2 py-1 text-xs text-red-800">
														0
													</span>
												{/if}
											</td>
										{/each}
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			{:else}
				<section class="p-4 text-center text-gray-500">
					<p>Парайс видалено</p>
				</section>
			{/if}
		{:catch error}
			<p class="text-center text-red-500">Помилка завантаження прайсу: {error.message}</p>
		{/await}
	</section>
</main>
