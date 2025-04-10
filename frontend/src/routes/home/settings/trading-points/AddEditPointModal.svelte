<script lang="ts">
	import { enhance } from '$app/forms';
	import { Dialog } from 'bits-ui';
	import { onMount } from 'svelte';
	import type { ActionData } from './$types';
	import toast from 'svelte-french-toast';

	interface Props {
		openState: boolean;
		nameAlreadyExists?: boolean;
		modalClose?: () => void;
		type: 'add' | 'edit';
		point?: {
			id: number;
			name: string;
			region: string;
			locality: string;
			street: string;
		};
		form?: ActionData;
	}

	let nameAlreadyExists = $state(false);

	let {
		openState = $bindable(false),
		modalClose = () => {
			nameAlreadyExists = false;
			openState = false;
		},
		type,
		form = $bindable(),
		point = $bindable()
	}: Props = $props();

	onMount(() => {
		console.log(point?.id);
		console.log(openState);
		nameAlreadyExists = false;
		form = undefined;
	});

	$effect(() => {
		if (!form) return;
		if (form.id !== point?.id && type === 'edit') return;
		nameAlreadyExists = form.message === 'name_already_exists';

		if (form.success) {
			modalClose();
			toast.success('Торгова точка успішно збережена');
		} else {
			toast.error('Ой, щось пішло не так');
		}
	});
</script>

<Dialog.Root bind:open={openState}>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed top-[50%] left-[50%] z-50 h-fit w-1/2 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="flex w-full justify-end">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="з-4 flex w-full items-center justify-end text-lg font-semibold tracking-tight"
			>
				{#if type === 'edit'}
					<h4 class="h5 w-full text-center">Редагування торгової точки</h4>
				{:else if type === 'add'}
					<h4 class="h5 w-full text-center">Додавання торгової точки</h4>
				{:else}
					<h4 class="h5 w-full text-center">Торгова точка</h4>
				{/if}
			</Dialog.Title>
			<Dialog.Description class="p-4">
				<form
					class="flex flex-col gap-10 px-10"
					method="POST"
					use:enhance={() => {
						return async ({ update }) => {
							update({ reset: false });
						};
					}}
				>
					<input type="hidden" name="id" value={point?.id} />
					<label class="label">
						<span class="text-lg">Назва</span>
						<input
							class="input h-16 border"
							class:border-error-400={nameAlreadyExists}
							name="name"
							type="text"
							placeholder="Введіть назву торогової точки"
							required
							value={point?.name}
						/>
						{#if nameAlreadyExists}
							<p class="text-error-400">Торгова точка з такою назвою вже існує</p>
						{/if}
					</label>
					<label class="label">
						<span class="text-lg">Область</span>
						<input
							class="input h-16 border"
							name="region"
							type="text"
							placeholder="Оберіть область"
							required
							value={point?.region}
						/>
					</label>
					<label class="label">
						<span class="text-lg">Населений пункт</span>
						<input
							class="input h-16 border"
							name="locality"
							type="text"
							placeholder="Оберіть наслений пункт"
							required
							value={point?.locality}
						/>
					</label>
					<label class="label">
						<span class="text-lg">Вулиця</span>
						<input
							class="input h-16 border"
							name="street"
							type="text"
							placeholder="Введіть назву вулиці"
							required
							value={point?.street}
						/>
					</label>
					<div class="flex justify-end gap-4">
						<button
							type="button"
							class="btn preset-outlined-primary-950-50 text-xl"
							onclick={modalClose}>Скасувати</button
						>
						{#if type === 'edit'}
							<button
								type="submit"
								formaction="?/editTradingPoint"
								class="btn preset-filled-primary-950-50 text-xl">Зберегти</button
							>
						{:else if type === 'add'}
							<button
								type="submit"
								formaction="?/addTradingPoint"
								class="btn preset-filled-primary-950-50 text-xl">Додати</button
							>
						{/if}
					</div>
				</form>
			</Dialog.Description>
			<Dialog.Close />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
