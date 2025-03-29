<script lang="ts">
	import { Dialog } from 'bits-ui';

	interface Props {
		point?: {
			id: number;
			name: string;
			region: string;
			locality: string;
			street: string;
		};
		open: boolean;
	}

	let { point, open = $bindable() }: Props = $props();

	let modalClose = () => {
		open = false;
	};

	console.log(point);
</script>

<Dialog.Root {open}>
	<Dialog.Portal>
		<Dialog.Overlay
			class="data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 fixed inset-0 z-50 bg-black/80"
		/>
		<Dialog.Content
			class="fixed top-[50%] left-[50%] z-50 translate-x-[-50%] translate-y-[-50%] rounded-xl bg-white p-4"
		>
			<div class="flex w-full justify-end">
				<button type="button" class="preset-tonal-surface-100" onclick={modalClose}>
					<img src="/close-icon.svg" alt="close" class="size-4" />
				</button>
			</div>
			<Dialog.Title
				class="flex w-full items-center justify-end p-4 text-lg font-semibold tracking-tight"
			>
				<h4 class="h5 w-full text-center">
					Ви впевнені, що хочете видалити торгову точку "{point?.name}"?
				</h4>
			</Dialog.Title>
			<Dialog.Description class="p-4">
				<p class="text-surface-500 text-center">
					Після видалення торгової точки, ви не зможете відновити її.
				</p>
				<form method="POST" action="?/deleteTradingPoint" class="mt-5">
					<input type="hidden" name="id" value={point?.id} />
					<div class="flex items-center justify-end gap-3">
						<button
							type="button"
							class="btn btn-lg preset-outlined-primary-950-50 font-bold"
							onclick={modalClose}>Скасувати</button
						>
						<button type="submit" class="btn btn-lg preset-filled-error-700-300 font-bold"
							>Видалити</button
						>
					</div>
				</form>
			</Dialog.Description>
			<Dialog.Close />
		</Dialog.Content>
	</Dialog.Portal>
</Dialog.Root>
