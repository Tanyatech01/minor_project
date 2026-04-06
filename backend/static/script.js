gsap.registerPlugin(ScrollTrigger);

let tvWidget = null;

function initChart(symbol) {
    if (tvWidget !== null) {
        document.getElementById("tv_chart_container").innerHTML = "";
    }
    tvWidget = new TradingView.widget({
        autosize: true,
        symbol: symbol,
        interval: "D",
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "en",
        enable_publishing: false,
        backgroundColor: "#0a0a0a",
        gridColor: "#1a1a1a",
        hide_top_toolbar: true,
        hide_legend: true,
        save_image: false,
        container_id: "tv_chart_container",
        toolbar_bg: "#0a0a0a",
    });
}

function loadChart(e, symbol, name) {
    const btns = document.querySelectorAll(".market-section .beveled-btn");
    btns.forEach((b) => {
        if (
            !b.classList.contains("outline-btn") &&
            b.innerText !== "Search Symbol"
        ) {
            b.classList.add("outline-btn");
        }
    });
    e.target.classList.remove("outline-btn");
    document.getElementById("asset-title").innerText = name;

    document.getElementById("stat-mcap").innerText = "Live Syncing...";
    document.getElementById("stat-vol").innerText = "Live Syncing...";
    document.getElementById("stat-util").innerText = "Analyzing...";

    setTimeout(() => {
        document.getElementById("stat-mcap").innerText = symbol.includes("BTC")
            ? "$1.2T"
            : symbol.includes("ETH")
              ? "$450B"
              : "$150B+";
        document.getElementById("stat-vol").innerText = symbol.includes("BTC")
            ? "$45.8B"
            : symbol.includes("ETH")
              ? "$20.1B"
              : "$5.2B";
        document.getElementById("stat-util").innerText =
            symbol.includes("IBM") || symbol.includes("MSFT")
                ? "Enterprise"
                : "High";
    }, 800);

    initChart(symbol);
}

function searchCustomChart() {
    const val = document.getElementById("tvSearch").value.trim().toUpperCase();
    if (!val) return;

    const btns = document.querySelectorAll(".market-section .beveled-btn");
    btns.forEach((b) => {
        if (
            !b.classList.contains("outline-btn") &&
            b.innerText !== "Search Symbol"
        ) {
            b.classList.add("outline-btn");
        }
    });

    document.getElementById("asset-title").innerText =
        val + " (Custom Analysis)";
    document.getElementById("stat-mcap").innerText = "Tracking...";
    document.getElementById("stat-vol").innerText = "Tracking...";
    document.getElementById("stat-util").innerText = "Live Search";

    initChart(val);
}

function rT() {
    gsap.utils.toArray(".scroll-tile").forEach((t) => {
        gsap.to(t, {
            scrollTrigger: {
                trigger: t,
                start: "top 85%",
                toggleActions: "play none none reverse",
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            ease: "power3.out",
        });
    });

    gsap.utils.toArray(".tech-table tbody tr").forEach((tr, i) => {
        gsap.to(tr, {
            scrollTrigger: {
                trigger: ".tech-table",
                start: "top 80%",
            },
            opacity: 1,
            x: 0,
            duration: 0.5,
            delay: i * 0.1,
            ease: "power2.out",
            startAt: { opacity: 0, x: -30 },
        });
    });
}

function s(x) {
    document.querySelectorAll(".content").forEach((y) => {
        y.classList.remove("active");
        gsap.killTweensOf(y.querySelectorAll(".scroll-tile"));
        y.querySelectorAll(".scroll-tile").forEach((t) => {
            gsap.set(t, { opacity: 0, y: 50 });
        });
    });

    document.getElementById(x).classList.add("active");

    if (x === "home") {
        document.getElementById("main-bg").classList.add("show");
        document.getElementById("news-ticker").style.display = "flex";
        if (document.getElementById("tv_chart_container").innerHTML === "") {
            initChart("BINANCE:BTCUSD");
        }
    } else {
        document.getElementById("main-bg").classList.remove("show");
        document.getElementById("news-ticker").style.display = "none";
    }

    gsap.from("#" + x, { opacity: 0, y: 20, duration: 0.5 });
    setTimeout(rT, 50);
}

function o(x) {
    document.getElementById(x).style.display = "block";
    gsap.from("#" + x + " .modalbox", {
        scale: 0.8,
        opacity: 0,
        duration: 0.4,
        ease: "back.out(1.5)",
    });
}

function c(x) {
    gsap.to("#" + x + " .modalbox", {
        scale: 0.8,
        opacity: 0,
        duration: 0.3,
        onComplete: () => {
            document.getElementById(x).style.display = "none";
        },
    });
}

window.onclick = (e) => {
    document.querySelectorAll(".modal").forEach((m) => {
        if (e.target == m) c(m.id);
    });
};

window.onload = () => {
    rT();
    gsap.from(".hero-quote", {
        opacity: 0,
        scale: 0.95,
        duration: 1,
        delay: 0.2,
    });

    if (document.getElementById("home").classList.contains("active")) {
        initChart("BINANCE:BTCUSD");
    }
};
