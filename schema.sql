create table if not exists public.mensajes_procesados (
    message_id text primary key,
    telefono text not null,
    recibido_en timestamptz not null default now(),
    categoria text
);

alter table public.mensajes_procesados add column if not exists categoria text;