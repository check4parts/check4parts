<script lang="ts">
	const advantages = [
		{
			icon: '/efficiency-icon.svg',
			title: 'Покращення ефективності',
			content:
				'Від пошуку запчастин до фінансових розрахунків і доставки — все доступно через єдиний інтерфейс.'
		},
		{
			icon: '/time-money-icon.svg',
			title: 'Економія часу та коштів',
			content:
				'Завдяки зручному пошуку, фільтрації та порівнянню цін, ви швидко знайдете найкращі варіанти за вигідною ціною.'
		},
		{
			icon: '/interface-icon.svg',
			title: 'Зручний інтерфейс',
			content:
				'Простий і зрозумілий інтерфейс допомагає без зайвих зусиль знаходити потрібні деталі та здійснювати покупки.'
		}
	];
</script>

<div class="container mx-auto px-4 relative">
	<h2 class="h1 text-primary-950 mb-12 text-center">Наші переваги</h2>
	<div class="mx-auto flex max-w-6xl flex-col gap-8 px-10">
		{#each advantages as advantage, index}
			<div class="flex flex-col items-center gap-3 rounded-xl z-10 md:flex-row" class:md:justify-end={index % 2 === 1}>
				<img
					src={advantage.icon}
					alt={advantage.title}
					loading="lazy"
					class="bg-primary-950 size-20 rounded-2xl p-2 shadow-md"
				/>
				<div class="w-full text-center md:w-3/7 md:text-left">
					<h3 class="h4 text-primary-900 font-semibold">{advantage.title}</h3>
					<p class="text-surface-600 leading-relaxed">{advantage.content}</p>
				</div>
			</div>
		{/each}
	</div>
	<!-- Фоновий текст -->
	<span
		class="absolute inset-0 flex items-center justify-center md:text-[12vw] text-[20vw] font-extrabold text-surface-50 tracking-widest select-none"
	>
		CHECK4PARTS
	</span>
</div>
