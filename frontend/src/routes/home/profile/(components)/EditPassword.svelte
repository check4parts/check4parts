<script lang="ts">
	import { enhance } from '$app/forms';
	import { Dialog } from 'bits-ui';
	import type { ActionData } from '../$types';

	interface Props {
		openState: boolean;
		modalClose?: () => void;
		form?: ActionData;
	}

	let {
		openState = $bindable(false),
		modalClose = () => {
			openState = false;
		},
		form = $bindable(),
	}: Props = $props();

	let loading = $state(false);

	$effect(() => {
		loading = false;
	});
</script>

<Dialog.Root bind:open={openState}>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed left-[50%] top-[50%] z-50 h-fit w-1/3 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="flex w-full justify-end">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="p-4 flex w-full items-center justify-end text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">Скинути пароль</h4>
			</Dialog.Title>
			<Dialog.Description class="p-4">
				<form
					class="flex flex-col gap-5"
					method="POST"
					use:enhance={() => {
						return async ({ update }) => {
							update({ reset: false });
						};
					}}
					action="?/resetPassword"
					onsubmit={() => (loading = true)}
				>
					<div class="flex justify-end gap-4">
						<button
							type="button"
							class="btn preset-outlined-primary-950-50 text-xl"
							onclick={modalClose}>Скасувати</button
						>
						<button
							type="submit"
							class="btn preset-filled-error-950-50 text-xl"
							>{#if loading}
								Завантаження...
							{:else}
								Скинути
							{/if}</button
						>
					</div>
				</form>
			</Dialog.Description>
			<Dialog.Close />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
