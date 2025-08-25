<script lang="ts">
	import { afterNavigate } from '$app/navigation';

	const { data } = $props();
	const { warehouses, query, data: results, fetchError } = $derived(data);
	$inspect(data);
	let isLoading = $state(false);

	afterNavigate(() => {
		isLoading = false;
	});

	const formatPrice = (price: number) => {
		return new Intl.NumberFormat('uk-UA', {
			style: 'currency',
			currency: 'UAH',
			minimumFractionDigits: 2
		}).format(price);
	};

	const getWarehouse = (id: string | number) => {
		return warehouses?.find((w) => w.id === id);
	};

	// Групуємо спочатку за брендами, потім за артикулами
	const groupedData = $derived(
		results?.reduce(
			(acc, item) => {
				const brand = item.brand || 'Інші';
				const article = item.article || 'Без артикулу';

				if (!acc[brand]) {
					acc[brand] = {};
				}

				if (!acc[brand][article]) {
					acc[brand][article] = {
						items: [],
						providers: new Set<string>(),
						warehouses: new Map<string, number>()
					};
				}

				acc[brand][article].items.push(item);
				if (item.providers?.name) {
					acc[brand][article].providers.add(item.providers.name);
				}

				Object.entries(item.rests || {}).forEach(([whId, qty]) => {
					const quantity = Number(qty) || 0;
					if (quantity > 0) {
						const current = acc[brand][article].warehouses.get(whId) || 0;
						acc[brand][article].warehouses.set(whId, current + quantity);
					}
				});

				return acc;
			},
			{} as Record<
				string,
				Record<
					string,
					{
						items: (typeof results)[0][];
						providers: Set<string>;
						warehouses: Map<string, number>;
					}
				>
			>
		)
	);

	$inspect(groupedData, {
		name: 'Grouped Price Data',
		enabled: Boolean(groupedData)
	});

	const sortedBrands = $derived(groupedData ? Object.keys(groupedData).sort() : []);
</script>

<div class="space-y-6">
	<!-- Пошукова форма -->
	<div class="border-primary-950 rounded-xl border-2 bg-white p-4 shadow-sm">
		<form method="get" class="flex flex-col gap-3 sm:flex-row" onsubmit={() => (isLoading = true)}>
			<input
				type="text"
				name="q"
				placeholder="🔍 Введіть артикул, бренд або опис"
				value={query}
				class="border-primary-300 focus:border-primary-500 focus:ring-primary-200 flex-1 rounded-lg border-2 p-3 transition focus:ring-2 focus:outline-none"
			/>
			<button
				type="submit"
				class="bg-primary-600 hover:bg-primary-700 rounded-lg px-6 py-3 text-white shadow-md transition-colors hover:shadow-lg"
				disabled={isLoading}
			>
				{isLoading ? 'Шукаємо...' : 'Знайти товари'}
			</button>
		</form>
	</div>

	<!-- Стан завантаження -->
	{#if isLoading}
		<div class="border-primary-200 bg-primary-50 animate-pulse rounded-xl border-2 p-4">
			Пошук...
		</div>

		<!-- Помилка -->
	{:else if fetchError}
		<div class="rounded-xl border-2 border-red-200 bg-red-50 p-6 text-red-700">
			<div class="flex items-center gap-3">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-6 w-6"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<div>
					<h3 class="font-bold">Помилка при завантаженні</h3>
					<p class="text-sm">{fetchError.message}</p>
				</div>
			</div>
		</div>

		<!-- Результати -->
	{:else if query && groupedData}
		{#if sortedBrands.length > 0}
			<div class="max-h-[70vh] space-y-8 overflow-y-auto">
				{#each sortedBrands as brand}
					<div class="border-primary-200 overflow-hidden rounded-xl border-2 bg-white">
						<!-- Заголовок бренду -->
						<div class="bg-primary-100 border-primary-200 border-b p-3">
							<h3 class="text-primary-900 text-xl font-bold">{brand}</h3>
						</div>

						<div class="space-y-4 p-4">
							{#each Object.entries(groupedData[brand]) as [article, group]}
								<div class="border-primary-100 overflow-hidden rounded-lg border bg-white">
									<!-- Заголовок артикулу -->
									<div class="bg-primary-50 border-primary-100 border-b p-3">
										<div class="flex items-center justify-between">
											<h4 class="text-lg font-bold">{article}</h4>
											<span class="text-primary-600 text-sm">
												{group.items.length}
												{group.items.length === 1 ? 'варіант' : 'варіанти'}
											</span>
										</div>
									</div>
									<!-- Таблиця з наявністю та цінами -->
									<div class="p-3">
										<div class="space-y-2 text-sm">
											{#each group.items as item}
												{#each Object.entries(item.rests || {}) as [whId, quantity]}
													<div class="border-primary-100 grid grid-cols-4 items-center gap-3 py-1">
														<!-- Постачальник -->
														<div class="font-medium">
															{item.providers?.name || 'Невідомо'}
															{#if item.providers?.short_name}
																<span class="text-primary-500 text-xs"
																	>({item.providers.short_name})</span
																>
															{/if}
														</div>

														<!-- Склад -->
														<div>
															{getWarehouse(whId)?.name || 'Невідомий склад'}
															{#if getWarehouse(whId)?.short_name}
																<span class="text-primary-500 text-xs"
																	>({getWarehouse(whId)?.short_name})</span
																>
															{/if}
														</div>

														<!-- Кількість -->
														<div class="text-primary-600">
															{#if quantity === null || quantity === undefined}
																<span class="text-red-500">Невідомо</span>
															{:else}
																{quantity !== '' && quantity !== '0'
																	? `${quantity.toLocaleString()} шт.`
																	: 'немає'}
															{/if}
														</div>

														<!-- Ціна -->
														<div class="text-right font-medium">{formatPrice(item.price)}</div>
													</div>
												{/each}
											{/each}
										</div>
									</div>
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{:else}
			<div class="border-primary-200 rounded-xl border-2 bg-white p-6 text-center">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="text-primary-400 mx-auto h-12 w-12"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				<h3 class="mt-2 text-lg font-medium">Нічого не знайдено</h3>
				<p class="text-primary-600 mt-1">Спробуйте змінити параметри пошуку</p>
			</div>
		{/if}
	{/if}
</div>
