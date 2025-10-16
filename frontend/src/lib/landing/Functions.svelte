<script lang="ts">
	import { Accordion } from 'bits-ui';
	import { slide, fade, fly, scale } from 'svelte/transition';
	import { quintOut, elasticOut } from 'svelte/easing';

	let items = [
		{
			value: 'item-1',
			number: '01',
			title: 'Порівняння цін у реальному часі',
			content:
				'Актуальні ціни та наявність запчастин — завжди під рукою. Система автоматично оновлює інформацію, що дозволяє порівнювати пропозиції від різних постачальників.',
			image: '/feature-1.png'
		},
		{
			value: 'item-2',
			number: '02',
			title: 'Пошук за різними критеріями',
			content: 'Легко знаходьте потрібні запчастини за допомогою різноманітних методів пошуку:',
			bullets: [
				'За маркою та моделлю авто;',
				'За агрегатами та вузлами;',
				'За оригінальними номерами;',
				'За артикулами замінників.'
			]
		},
		{
			value: 'item-3',
			number: '03',
			title: 'Відображення наявності у всіх постачальників за 1 клік',
			content:
				'Всі пошукові результати показано на одній сторінці. Ви можете порівняти ціни та вибрати найкращу пропозицію без зайвих зусиль.'
		},
		{
			value: 'item-4',
			number: '04',
			title: 'Зручне замовлення та повернення товару',
			content:
				'Єдиний інтерфейс для замовлення та повернення товару без необхідності переходити на інші вкладки. Швидкість і простота в кожному кроці.',
			image: '/feature-4.png'
		},
		{
			value: 'item-5',
			number: '05',
			title: 'Контроль доставки товару',
			content:
				"Користувачі можуть відслідковувати терміни доставки по кожному постачальнику окремо. Також ви отримуєте детальну інформацію про кур'єрські служби, які здійснюють доставку.",
			image: '/feature-5.png'
		},
		{
			value: 'item-6',
			number: '06',
			title: 'Фінансовий блок',
			bullets: [
				'Єдиний формат документів для зручності роботи;',
				'Формування фінансових звітів по періодах: взаєморозрахунки, звіти по оплатах, заборгованість на дату;',
				'Контроль дебіторської заборгованості у всіх постачальників та уніфікація;',
				'Здійснення оплати постачальнику з головної сторінки та формування QR-коду на оплату.'
			]
		}
	];
</script>

<div class="container mx-auto py-8">
	<div class="bg-primary-950 text-surface-50 mx-auto max-w-5xl sm:rounded-3xl p-8">
		<!-- Header -->
		<div class="mb-8 text-center">
			<h2 class="text-2xl font-bold">Основні функції</h2>
		</div>

		<Accordion.Root type="single" class="space-y-1">
			{#each items as item}
				<Accordion.Item value={item.value} class="border-surface-50 border-b last:border-b-0">
					<Accordion.Header>
						<Accordion.Trigger
							class="group flex w-full items-start justify-between py-6 text-left transition-opacity duration-200 hover:opacity-80"
						>
							<div class="flex flex-1 items-center space-x-4 pr-4">
								<div class="min-w-[2rem] text-lg font-bold transition-transform duration-200">
									{item.number}
								</div>

								<!-- Title -->
								<h3
									class="group-hover:text-primary-300 text-lg font-bold transition-colors duration-200"
								>
									{item.title}
								</h3>
							</div>

							<div class="ml-2 mt-1 flex-shrink-0">
								<div
									class="flex h-8 w-8 items-center justify-center rounded-full transition-all duration-200 group-hover:scale-110 group-hover:bg-white/20"
								>
									<svg
										class="h-4 w-4 transform transition-transform duration-300 group-data-[state=open]:rotate-180"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M19 9l-7 7-7-7"
										/>
									</svg>
								</div>
							</div>
						</Accordion.Trigger>
					</Accordion.Header>

					<!-- Content with Svelte transitions -->
					<Accordion.Content forceMount={true} class="overflow-hidden">
						{#snippet child({ props, open })}
							<div {...props}>
								{#if open}
									<div
										class="pb-6 pl-12 pr-4"
										transition:slide={{ duration: 400, easing: quintOut }}
									>
										<!-- Main content area with staggered animations -->
										<div class="flex flex-col gap-6 lg:flex-row">
											<!-- Text content with fade + fly -->
											<div
												class="flex-1"
												in:fly={{ y: 20, duration: 300, delay: 100, easing: quintOut }}
												out:fade={{ duration: 200 }}
											>
												{#if item.content}
													<p class="mb-4 leading-relaxed">
														{item.content}
													</p>
												{/if}

												<!-- Bullet points with individual animations -->
												{#if item.bullets}
													<ul class="space-y-2">
														{#each item.bullets as bullet, index}
															<li
																class="flex items-start"
																in:fly={{
																	x: -20,
																	duration: 300,
																	delay: 200 + index * 50,
																	easing: quintOut
																}}
																out:fade={{ duration: 150 }}
															>
																<span class="mr-2">•</span>
																<span>{bullet}</span>
															</li>
														{/each}
													</ul>
												{/if}
											</div>

											{#if item.image}
												<div
													class="flex-shrink-0"
													in:scale={{
														duration: 400,
														delay: 200,
														start: 0.9,
														opacity: 0.8,
														easing: elasticOut
													}}
													out:scale={{
														duration: 200,
														start: 0.95,
														opacity: 0
													}}
												>
													<div class="rounded-lg bg-white/5">
														<img
															src={item.image}
															alt={item.title}
															class="h-auto w-full rounded shadow-lg"
															loading="lazy"
														/>
													</div>
												</div>
											{/if}
										</div>
									</div>
								{/if}
							</div>
						{/snippet}
					</Accordion.Content>
				</Accordion.Item>
			{/each}
		</Accordion.Root>
	</div>
</div>
