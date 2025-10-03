<script lang="ts">
	const features = [
		{
			icon: '/gear-1.svg',
			content: 'Магазини, що займаються продажем автозапчастин'
		},
		{
			icon: '/gear-2.svg',
			content: 'Незалежні станції технічного обслуговування'
		},
		{
			icon: '/gear-3.svg',
			content: 'Компанії, що обслуговують власні автопарки'
		}
	];
</script>

<div class="container mx-auto">
	<h2 class="h1 mb-8 text-center">Цільва аудиторія</h2>
	<div class="grid grid-cols-1 max-w-6xl mx-auto gap-8 md:grid-cols-3">
		{#each features as f}
			<div class="flex flex-col items-center space-y-4 text-center">
				<img src={f.icon} alt={f.content} loading="lazy" />
				<p class="text-primary-900 text-xl font-semibold w-2/3">{f.content}</p>
			</div>
		{/each}
	</div>
</div>
