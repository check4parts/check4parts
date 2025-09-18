export const IMPORTANT_HEADERS: TemplateRow[] = [
	{
		name: 'Бренд',
		value: 'brand',
		type: 'prop',
		header: '',
		aliases: ['brand', 'марка', 'бренд']
	},
	{
		name: 'Код Бренду',
		value: 'article',
		type: 'prop',
		header: '',
		aliases: [
			'артикул',
			'код',
			'код бренду',
			'CatItemNo',
			'номер',
			'Номер за каталогом постачальника'
		]
	},
	{
		name: 'Ціна',
		value: 'price',
		type: 'prop',
		header: '',
		aliases: ['ціна', 'вартість', 'price', 'Ваша ціна']
	},
	{
		name: 'Опис',
		value: 'description',
		type: 'prop',
		header: '',
		aliases: ['опис', 'опис товару', 'description', 'назва', 'назва товару', 'name']
	}
];

export type TemplateRow = {
	name: string;
	value: string;
	type: 'rests' | 'prop';
	header: string;
	aliases?: string[];
};

export type Template = {
	template: TemplateRow[];
	metadata: {
		firstRowHeaders: boolean;
		providerId?: string;
	};
};

export function autoMapHeaders(
  headers: string[],
  provider_warehouses: { id: string; name: string }[],
  savedTemplate?: TemplateRow[]
): TemplateRow[] {
	console.log('AutoMap Headers', savedTemplate);
  const normalize = (str: string) => str.toLowerCase().replace(/\s+/g, '');

  const matchImportant = (target: string, aliases: string[] = []) => {
    const candidates = [target, ...aliases].map(normalize);
    const idx = headers.findIndex((h) => candidates.includes(normalize(h)));
    return idx !== -1 ? idx.toString() : '';
  };

  const match = (target: string) => {
    const idx = headers.findIndex((h) => normalize(h).includes(normalize(target)));
    return idx !== -1 ? idx.toString() : '';
  };

  const findSavedHeader = (value: string): string | undefined => {
		console.log('Saved Template:', savedTemplate);
    return savedTemplate?.find((item) => item.value === value)?.header;
  };

  const props = IMPORTANT_HEADERS.map((h) => ({
    ...h,
    header: findSavedHeader(h.value) ?? matchImportant(h.name, h.aliases)
  }));

  const rests = provider_warehouses.map((wh) => ({
    name: wh.name,
    value: wh.id,
    type: 'rests' as const,
    header: findSavedHeader(wh.id) ?? match(wh.name)
  }));

  return [...props, ...rests];
}
