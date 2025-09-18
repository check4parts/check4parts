<script lang="ts">
	interface Props {
		step: number;
		stepState: 'current' | 'error' | 'success';
	}
	let steps = ['Завантажити файл', 'Перевірити дані', 'Завершити'];

	let { step = $bindable(), stepState }: Props = $props();
</script>

{#snippet stepElement(
	stepNumber: number,
	stepLable: string,
	stepState?: 'current' | 'error' | 'success'
)}
	{@const backgroundColor = stepState
		? stepState === 'current'
			? 'bg-surface-200'
			: stepState === 'error'
				? 'bg-error-500'
				: 'bg-success-600'
		: 'bg-surface-100'}
	<li>
		<div class="text-surface-50-950 flex items-center">
			<span class={backgroundColor + ' h-1 w-24'}></span>
			<button
				class={backgroundColor +
					' flex h-10 w-10 items-center justify-center rounded-full text-xl font-bold'}
				onclick={() => {
					step = stepNumber;
				}}
				disabled={step < stepNumber}
			>
				{stepNumber}
			</button>
			<span class={backgroundColor + ' h-1 w-24'}></span>
		</div>
		<p class="mt-2 text-center" class:font-bold={stepState === 'current'}>{stepLable}</p>
	</li>
{/snippet}

<ul class="flex items-center">
	{#each steps as stepLable, index}
		{@const currentState =
			index + 1 === step ? stepState : index + 1 < step ? 'success' : undefined}
		{@render stepElement(index + 1, stepLable, currentState)}
	{/each}
</ul>
